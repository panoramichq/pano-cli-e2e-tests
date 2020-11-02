from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from panoramic.cli import cli
from panoramic.cli.paths import FileExtension, PresetFileName, Paths

TEST_DATASET = """
dataset_slug: test_dataset
display_name: Test Dataset
"""

TEST_MODEL = """
api_version: v1
model_name: test_model
data_source: pano_snowflake_66.snowflake_sample_data.tpch_sf1.nation
fields:
  - field_map:
      - name
    data_reference: '"N_NAME"'
joins:
  - to_model: other_model
    relationship: many_to_one
    join_type: left
    fields:
      - name
identifiers:
  - name
"""

TEST_COMPANY_FIELD = """
api_version: v1
slug: company_test_field
display_name: Company test field
group: Custom
field_type: dimension
data_type: text
"""

TEST_DATASET_FIELD = """
api_version: v1
slug: dataset_test_field
display_name: Dataset test field
group: Custom
field_type: metric
data_type: text
"""


@pytest.mark.vcr
def test_push_pull_e2e(monkeypatch):
    monkeypatch.chdir(Path('e2e') / 'scenarios' / 'pano-push-pull')
    dataset_dir = Path('test_dataset')
    dataset_file: Path = dataset_dir / PresetFileName.DATASET_YAML.value
    model_file: Path = dataset_dir / f'test_model{FileExtension.MODEL_YAML.value}'

    # Create dataset scoped field
    company_fields_dir = Paths.fields_dir(Path.cwd())
    company_fields_dir.mkdir(exist_ok=True)
    company_field_file: Path = company_fields_dir / f'company_test_field{FileExtension.FIELD_YAML.value}'
    company_field_file.write_text(TEST_COMPANY_FIELD)

    # Create dataset and model to push
    dataset_dir.mkdir(exist_ok=True)
    dataset_file.write_text(TEST_DATASET)
    model_file.write_text(TEST_MODEL)
    # Create dataset scoped field
    dataset_fields_dir = Paths.fields_dir(dataset_dir)
    dataset_fields_dir.mkdir(exist_ok=True)

    dataset_field_file: Path = dataset_fields_dir / f'dataset_test_field{FileExtension.FIELD_YAML.value}'
    dataset_field_file.write_text(TEST_DATASET_FIELD)

    # Push dataset and model
    runner = CliRunner()
    result = runner.invoke(cli, ['push', '-y'])

    # Check push was successful
    assert result.exit_code == 0

    # Delete local files so they can be re-created with pull
    dataset_file.unlink()
    model_file.unlink()
    company_field_file.unlink()
    dataset_field_file.unlink()

    # Pull dataset and model
    result = runner.invoke(cli, ['pull', '-y'])

    # Check pull was successful
    assert dataset_file.exists()
    assert model_file.exists()
    assert dataset_field_file.exists()
    assert company_field_file.exists()

    # Delete local dataset and model files
    dataset_file.unlink()
    model_file.unlink()
    company_field_file.unlink()
    dataset_field_file.unlink()

    # Push deleted dataset and model
    result = runner.invoke(cli, ['push', '-y'])

    # Check push was successful
    assert result.exit_code == 0


@pytest.mark.vcr
@patch('panoramic.cli.command.push')
def test_push_error_e2e(mock_push, monkeypatch):
    monkeypatch.chdir(Path('e2e') / 'scenarios' / 'pano-push-pull')
    mock_push.side_effect = Exception('Test Exception')

    runner = CliRunner()
    result = runner.invoke(cli, ['push'])

    assert result.exit_code == 1
    assert result.stdout.startswith('Error: Internal error occurred\nTraceback (most recent call last):\n')
    assert result.stdout.endswith('raise effect\nException: Test Exception\n\n')


@pytest.mark.vcr
@patch('panoramic.cli.command.pull')
def test_pull_error_e2e(mock_pull, monkeypatch):
    monkeypatch.chdir(Path('e2e') / 'scenarios' / 'pano-push-pull')
    mock_pull.side_effect = Exception('Test Exception')

    runner = CliRunner()
    result = runner.invoke(cli, ['pull'])

    assert result.exit_code == 1
    assert result.stdout.startswith('Error: Internal error occurred\nTraceback (most recent call last):\n')
    assert result.stdout.endswith('raise effect\nException: Test Exception\n\n')
