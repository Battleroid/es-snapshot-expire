# es-snapshot-expire

Expires snapshots for multiple clusters, forcibly. Curator will not do this as you expect, it instead errors out the moment it cannot connect or has issues deleting. It will not retry accordingly. This will ignore any and all exceptions except for a 404 on deletion. 404 on deletion means the snapshot no longer exists and is finished deleting.

## Usage

```
usage: expire.py [-h] [--version] [--for-real] config

Expire snapshots forcibly, unlike curator.

positional arguments:
  config      Config file.

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  --for-real  delete for real
```

See the [sample](sample.yaml) for a sample setup against multiple clusters.
