from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from panoramic.cli import cli
from panoramic.cli.paths import Paths


@pytest.mark.vcr
def test_connections_e2e(monkeypatch, tmpdir):
    monkeypatch.setattr(Path, 'home', lambda: str(tmpdir))
    runner = CliRunner()

    # Create config
    runner.invoke(cli, ['configure'], input='test-client-id\ntest-client-secret')

    # Create connection
    result = runner.invoke(
        cli,
        [
            'connection',
            'create',
            'my-connection', '--type', 'postgres',
            '--user',
            'my-user',
            '--host',
            'localhost',
            '--port',
            '5432',
            '--database',
            'my_db',
            '--password-stdin',
            '--no-test',
        ],
        input='my-password',
    )

    assert result.exit_code == 0, result.output
    connections_json = {
            'auth': {
                'client_id': 'test-client-id',
                'client_secret': 'test-client-secret',
            },
            'connections': {
                'my-connection': {
                    'type': 'postgres',
                    'user': 'my-user',
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'my_db',
                    'password': 'my-password',
                },
            },
        }
    with Paths.config_file().open() as f:
        assert yaml.safe_load(f.read()) == connections_json

    # List
    result = runner.invoke(cli, ['connection', 'list', '--show-password'])
    assert result.exit_code == 0, result.output
    assert result.output == yaml.dump(connections_json['connections']) + "\n"

    # Update
    result = runner.invoke(cli, ['connection', 'update', 'my-connection', '--database', 'my-new-db',
                                 '--no-test'])
    assert result.exit_code == 0, result.output

    # List
    result = runner.invoke(cli, ['connection', 'list'])
    assert result.exit_code == 0, result.output
    connections_json['connections']['my-connection']['password'] = '*****'
    connections_json['connections']['my-connection']['database'] = 'my-new-db'
    assert result.output == yaml.dump(connections_json['connections']) + "\n"

    # Update
    result = runner.invoke(cli, ['connection', 'remove', 'my-connection'])
    assert result.exit_code == 0, result.output

    # List
    result = runner.invoke(cli, ['connection', 'list'])
    assert result.exit_code == 0, result.output
    assert result.stdout.startswith('No connections found.\nUse "pano connection create" to create')


@pytest.mark.vcr
def test_connections_list_fail_e2e(monkeypatch, tmpdir):
    monkeypatch.setattr(Path, 'home', lambda: str(tmpdir))
    runner = CliRunner()

    # Create config
    runner.invoke(cli, ['configure'], input='test-client-id\ntest-client-secret')

    # List connections
    result = runner.invoke(cli, ['connection', 'list'])
    assert result.exit_code == 0, result.output
    assert result.stdout.startswith('No connections found.\nUse "pano connection create" to create')


@pytest.mark.vcr
def test_connections_update_fail_e2e(monkeypatch, tmpdir):
    monkeypatch.setattr(Path, 'home', lambda: str(tmpdir))
    runner = CliRunner()

    # Create config
    runner.invoke(cli, ['configure'], input='test-client-id\ntest-client-secret')

    # Update connection
    result = runner.invoke(cli, ['connection', 'update', 'my-connection'])
    assert result.exit_code == 1, result.output
    assert result.stdout.endswith('Error: Connection with name "my-connection" was not found.\n')
