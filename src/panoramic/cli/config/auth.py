import os

from panoramic.cli.local.file_utils import read_yaml
from panoramic.cli.paths import Paths


def get_client_id_env_var() -> str:
    return os.environ['PANO_CLIENT_ID']


def get_client_secret_env_var() -> str:
    return os.environ['PANO_CLIENT_SECRET']


def get_client_id() -> str:
    try:
        return get_client_id_env_var()
    except KeyError:
        return read_yaml(Paths.config_file())['client_id']


def get_client_secret() -> str:
    try:
        return get_client_secret_env_var()
    except KeyError:
        return read_yaml(Paths.config_file())['client_secret']
