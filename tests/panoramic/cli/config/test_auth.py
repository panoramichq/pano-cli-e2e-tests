import tempfile

import pytest
import yaml

from panoramic.cli.config.auth import get_client_id, get_client_secret
from panoramic.cli.paths import Paths


@pytest.fixture(autouse=True)
def remove_client_creds_env(monkeypatch):
    monkeypatch.delenv('PANO_CLIENT_ID', raising=False)
    monkeypatch.delenv('PANO_CLIENT_SECRET', raising=False)


def test_env_vars(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirname:
        monkeypatch.setenv('HOME', tmpdirname)
        Paths.config_dir().mkdir()

        with Paths.config_file().open('w') as f:
            f.write(yaml.dump(dict(client_id='some_random_id', client_secret='some_random_secret')))

        monkeypatch.setenv('PANO_CLIENT_ID', 'test_client_id')
        monkeypatch.setenv('PANO_CLIENT_SECRET', 'test_client_secret')

        assert get_client_id() == 'test_client_id'
        assert get_client_secret() == 'test_client_secret'


def test_config_file(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirname:
        monkeypatch.setenv('HOME', tmpdirname)
        Paths.config_dir().mkdir()

        with Paths.config_file().open('w') as f:
            f.write(yaml.dump(dict(client_id='some_random_id', client_secret='some_random_secret')))

        assert get_client_id() == 'some_random_id'
        assert get_client_secret() == 'some_random_secret'
