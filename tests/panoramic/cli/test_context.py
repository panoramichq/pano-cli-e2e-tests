import yaml

from panoramic.cli.context import get_company_slug
from panoramic.cli.paths import Paths


def test_context_file(monkeypatch, tmpdir):
    monkeypatch.chdir(tmpdir)

    with open(Paths.context_file(), 'w') as f:
        f.write(yaml.dump(dict(api_version='v2', company_slug='company_name_12fxs')))

    assert get_company_slug() == 'company_name_12fxs'
