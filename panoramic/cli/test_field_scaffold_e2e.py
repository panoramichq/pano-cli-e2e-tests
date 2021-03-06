from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from panoramic.cli import cli
from panoramic.cli.paths import Paths


@pytest.fixture
def clear_fields(monkeypatch):
    monkeypatch.chdir(Path('e2e') / 'scenarios' / 'pano-field-scaffold')
    # delete field files
    for f in Paths.fields_dir(Path('test_dataset')).iterdir():
        f.unlink()
    yield


@pytest.mark.vcr
def test_field_scaffold_e2e(clear_fields):
    runner = CliRunner()
    result = runner.invoke(cli, ['field', 'scaffold', '-y'])

    fields_dir = Paths.fields_dir(Path('test_dataset'))

    assert result.exit_code == 0
    assert {f.name for f in fields_dir.iterdir()} == {'dataset_test_field.field.yaml'}
    assert (
        (fields_dir / 'dataset_test_field.field.yaml').read_text()
        == """api_version: v1
data_type: text
display_name: dataset_test_field
field_type: dimension
group: CLI
slug: dataset_test_field
"""
    )


@pytest.mark.vcr
@patch('panoramic.cli.command.scaffold_missing_fields')
def test_field_scaffold_error_e2e(mock_scaffold, monkeypatch):
    monkeypatch.chdir(Path('e2e') / 'scenarios' / 'pano-push-pull')
    mock_scaffold.side_effect = Exception('Test Exception')

    runner = CliRunner()
    result = runner.invoke(cli, ['field', 'scaffold'])

    assert result.exit_code == 1
    assert result.stdout.startswith('Error: Internal error occurred\nTraceback (most recent call last):\n')
    assert result.stdout.endswith('raise effect\nException: Test Exception\n\n')
