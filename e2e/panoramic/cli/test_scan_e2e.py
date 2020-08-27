from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from panoramic.cli import cli
from panoramic.cli.paths import Paths


@pytest.fixture(autouse=True)
def handle_scanned_dir(monkeypatch):
    test_dir = Path('e2e') / 'scenarios' / 'pano-scan'
    monkeypatch.chdir(test_dir)

    # Clean scanned directory
    for f in Paths.scanned_dir().glob('*'):
        f.unlink()

    yield

    # Clean scanned directory
    for f in Paths.scanned_dir().glob('*'):
        f.unlink()


def _drop_running_status(response):
    """Speed up execution of e2e by dropping status=RUNNING responses."""
    if b'RUNNING' in response['body']['string'] or b'METADATA_RETRIEVAL' in response['body']['string']:
        return None

    return response


@pytest.fixture(scope='module')
def vcr_config(vcr_config):
    def before_record_response(response):
        return _drop_running_status(vcr_config['before_record_response'](response))

    return {**vcr_config, 'before_record_response': before_record_response}


@pytest.mark.vcr
def test_scan_e2e():
    runner = CliRunner()

    result = runner.invoke(cli, ['scan', 'SF', '--parallel', '1', '--filter', 'METRICS3_STG.ADWORDS_VIEWS.ENTITY%'])

    assert result.exit_code == 0
    assert {f.name for f in Paths.scanned_dir().iterdir()} == {
        'sf.metrics3_stg.adwords_views.entity_accounts.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_adgroups.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_adgroups_from_service.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_ads.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_ads_from_service.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_advideos.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_campaigns.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_campaigns_criterion.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_campaigns_from_service.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_user_lists.model.yaml',
    }


@pytest.mark.vcr
def test_scan_id_generator_e2e():
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ['scan', 'SF', '--generate-identifiers', '--parallel', '1', '--filter', 'METRICS3_STG.ADWORDS_VIEWS.ENTITY%'],
    )

    assert result.exit_code == 0
    assert {f.name for f in Paths.scanned_dir().iterdir()} == {
        'sf.metrics3_stg.adwords_views.entity_accounts.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_adgroups.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_adgroups_from_service.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_ads.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_ads_from_service.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_advideos.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_campaigns.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_campaigns_criterion.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_campaigns_from_service.model.yaml',
        'sf.metrics3_stg.adwords_views.entity_user_lists.model.yaml',
    }


@pytest.mark.vcr
@patch('panoramic.cli.command.scan')
def test_scan_error_e2e(mock_scan):
    mock_scan.side_effect = Exception('Test Exception')
    runner = CliRunner()

    result = runner.invoke(cli, ['scan', 'SF', '--filter', 'METRICS3_STG.ADWORDS_VIEWS.ENTITY%'])

    assert result.exit_code == 1
    assert result.stdout.startswith('Error: Internal error occurred\nTraceback (most recent call last):\n')
    assert result.stdout.endswith('raise effect\nException: Test Exception\n\n')
