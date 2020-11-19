from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner

from panoramic.cli import cli
from panoramic.cli.paths import Paths


@pytest.mark.vcr
def test_configure_e2e(monkeypatch, tmpdir):
    monkeypatch.setattr(Path, 'home', lambda: tmpdir)
    runner = CliRunner()

    result = runner.invoke(cli, ['configure'], input='test-client-id\ntest-client-secret')

    assert result.exit_code == 0
    with Paths.config_file().open() as f:
        assert yaml.safe_load(f.read()) == {
            'auth': {
                'client_id': 'test-client-id',
                'client_secret': 'test-client-secret',
            },
        }


@pytest.mark.vcr
@patch('panoramic.cli.command.configure')
def test_configure_error_e2e(mock_configure, monkeypatch, tmpdir):
    monkeypatch.setattr(Path, 'home', lambda: tmpdir)
    runner = CliRunner()

    mock_configure.side_effect = Exception('Test Exception')

    result = runner.invoke(cli, ['configure'])

    assert result.exit_code == 1
    assert result.stdout.startswith('Error: Internal error occurred\nTraceback (most recent call last):\n')
    assert result.stdout.endswith('raise effect\nException: Test Exception\n\n')
