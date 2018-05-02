from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import find_packages, setup
from expire import __version__ as expire_version

reqs = parse_requirements('requirements.txt', session=PipSession())
requirements = [str(req.req) for req in reqs]

setup(
    name='es-snapshot-expire',
    author='Casey Weed',
    author_email='cweed@caseyweed.com',
    version=expire_version,
    description='Force those snapshots to die',
    url='https://github.com/battleroid/es-snapshot-expire',
    py_modules=['expire'],
    install_requires=[
        'elasticsearch-curator',
        'elasticsearch',
        'certifi',
        'pyyaml'
    ],
    entry_points="""
        [console_scripts]
        es-snapshot-expire=expire:run
    """
)
