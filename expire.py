import argparse
import logging
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import structlog
import yaml
from curator import SnapshotList
from elasticsearch import Elasticsearch


# sure, whatever
logging.basicConfig(format='%(message)s', stream=sys.stdout, level=logging.INFO)
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper('iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True
)

log = structlog.getLogger('expire')
logging.getLogger('elasticsearch').setLevel(100)


def delete_snapshots(cluster):

    # client setup
    auth = (cluster['username'], cluster['password'])
    es = Elasticsearch(cluster['url'], use_ssl=True, http_auth=auth, timeout=180, request_timeout=180)
    clog = log.bind(cluster=es.cluster.health()['cluster_name'])

    # filter snapshots
    slo = SnapshotList(es, repository=cluster['repository'])
    slo.filter_by_age(direction='older', unit='days', unit_count=int(cluster['older_than']))
    if not slo.working_list():
        clog.warn('no_snapshots', message='No snapshots found.')
        return
    clog.info('found_snapshots', snapshots_list=slo.working_list(), total=len(slo.working_list()))

    # delete snapshots, ignoring any/all exceptions except success (404, meaning it no longer exists)
    for i, snapshot in enumerate(slo.working_list()):
        start_time = time.time()
        clog.info('deleting_snapshot', snapshot=snapshot)
        while True:
            try:
                es.snapshot.delete(cluster['repository'], snapshot, request_timeout=20)
            except Exception as e:
                if e.status_code == 404:
                    break
                if e.status_code == 503:
                    time.sleep(30)
                time.sleep(10)
            else:
                break
        clog.info('deleted_snapshot', snapshot=snapshot, duration=time.time() - start_time)

    clog.info('finished')


def main(config):
    config = yaml.safe_load(os.path.expandvars(config.read_text()))

    # build config
    defaults = config.get('settings', {})
    for cluster in config['clusters']:
        for k, v in defaults.items():
            cluster.setdefault(k, v)

    log.info('built_config')

    # launch jobs
    with ThreadPoolExecutor() as tpe:
        for cluster in config['clusters']:
            tpe.submit(delete_snapshots, cluster)


parser = argparse.ArgumentParser(description='Expire snapshots forcibly, unlike curator.')
parser.add_argument('config', type=Path, default='config.yaml', help='Config file.')

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.config)
