import pytest
import yaml
from click.testing import CliRunner

from panoramic.cli import cli
from panoramic.cli.paths import Paths


@pytest.mark.vcr
def test_data_connections_e2e(monkeypatch, tmpdir):
    monkeypatch.setenv('HOME', str(tmpdir))
    runner = CliRunner()

    # Create
    result = runner.invoke(
        cli,
        [
            'data-connections',
            'create',
            'my-data-connection', '--type', 'postgres',
            '--user',
            'my-user',
            '--host',
            'localhost',
            '--port',
            '5432',
            '--database-name',
            'my_db',
            '--password-stdin',
            '--no-test',
        ],
        input='my-password',
    )

    assert result.exit_code == 0, result.output
    with Paths.config_file().open() as f:
        assert yaml.safe_load(f.read()) == {
            'data_connections': {
                'my-data-connection': {
                    'type': 'postgres',
                    'user': 'my-user',
                    'host': 'localhost',
                    'port': '5432',
                    'database_name': 'my_db',
                    'password': 'my-password',
                },
            },
        }

    # List
    result = runner.invoke(cli, ['data-connections', 'list'])
    assert result.exit_code == 0, result.output
    assert result.output == 'my-data-connection: postgres://my-user:*****@localhost:5432/my_db\n'

    # Update
    result = runner.invoke(cli, ['data-connections', 'update', 'my-data-connection', '--database-name', 'my-new-db',
                                 '--no-test'])
    assert result.exit_code == 0, result.output

    # List
    result = runner.invoke(cli, ['data-connections', 'list'])
    assert result.exit_code == 0, result.output
    assert result.output == 'my-data-connection: postgres://my-user:*****@localhost:5432/my-new-db\n'

    # Update
    result = runner.invoke(cli, ['data-connections', 'remove', 'my-data-connection'])
    assert result.exit_code == 0, result.output

    # List
    result = runner.invoke(cli, ['data-connections', 'list'])
    assert result.exit_code == 0, result.output
    assert result.stdout.startswith('No data connections found.\nUse "pano data-connections create" to create')


@pytest.mark.vcr
def test_data_connections_list_fail_e2e(monkeypatch, tmpdir):
    monkeypatch.setenv('HOME', str(tmpdir))
    runner = CliRunner()

    result = runner.invoke(cli, ['data-connections', 'list'])
    assert result.exit_code == 0, result.output
    assert result.stdout.startswith('No data connections found.\nUse "pano data-connections create" to create')


@pytest.mark.vcr
def test_data_connections_update_fail_e2e(monkeypatch, tmpdir):
    monkeypatch.setenv('HOME', str(tmpdir))
    runner = CliRunner()

    result = runner.invoke(cli, ['data-connections', 'update', 'my-data-connection'])
    assert result.exit_code == 1, result.output
    assert result.stdout.startswith('Error: Data connection with name "my-data-connection" not found.\n')
