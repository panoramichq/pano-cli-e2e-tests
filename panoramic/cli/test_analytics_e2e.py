import json
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner

from panoramic.cli import cli
from panoramic.cli.paths import Paths
from panoramic.cli import analytics
from panoramic.cli import command


@pytest.mark.vcr
def test_analytics_e2e(monkeypatch, tmpdir):
    flushed = False
    def flush_mock():
        nonlocal flushed
        flushed = True

    monkeypatch.setattr(Path, 'home', lambda: Path(tmpdir))
    monkeypatch.setattr(analytics, '_flush', flush_mock)
    # Enable writing of events
    monkeypatch.setattr(analytics, 'config_is_enabled', lambda: True)
    # Enabled prompt
    monkeypatch.setattr(command, 'analytics_module_is_enabled', lambda: True)
    runner = CliRunner()

    result = runner.invoke(cli, ['configure'], input='test-client-id\ntest-client-secret\ny')
    assert result.exit_code == 0, result.output
    with Paths.config_file().open() as f:
        assert yaml.safe_load(f.read()) == {
            'analytics': {
                'enabled': True,
            },
            'auth': {
                'client_id': 'test-client-id',
                'client_secret': 'test-client-secret',
            },
        }

    # Create connection
    result = runner.invoke(
        cli,
        [
            'connection',
            'create',
            'my-connection',
            '--type',
            'postgres',
            '--user',
            'my-user',
            '--host',
            'localhost',
            '--port',
            '5432',
            '--database',
            'my_db',
            '--password',
            'my-password',
            '--no-test',
        ],
    )
    assert result.exit_code == 0, result.output

    assert len(analytics._read_events()) == 1

    for i in range(analytics.MINIMAL_FLUSH_EVENTS):
        result = runner.invoke(
            cli, ['connection', 'update', 'my-connection', '--database', f'my-new-db-{i}', '--no-test']
        )
        assert result.exit_code == 0, result.output

    assert flushed is True
    assert len(analytics._read_events()) == 11

    with Paths.analytics_events_file().open() as f:
        lines = list(f.readlines())
        data = json.loads(lines[0])
        assert data['name'] == 'connection create'
        assert data['user_id'] == 'test-client-id'
        for line in lines[1:]:
            data = json.loads(line)
            assert data['name'] == 'connection update'
