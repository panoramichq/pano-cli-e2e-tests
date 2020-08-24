import os

from panoramic.cli.local.file_utils import read_yaml
from panoramic.cli.paths import Paths


def get_client_id() -> str:
    try:
        return os.environ['PANO_CLIENT_ID']
    except KeyError:
        return read_yaml(Paths.config_file())['client_id']


def get_client_secret() -> str:
    try:
        return os.environ['PANO_CLIENT_SECRET']
    except KeyError:
        return read_yaml(Paths.config_file())['client_secret']
