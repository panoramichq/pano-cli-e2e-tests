from panoramic.cli.local.file_utils import read_yaml
from panoramic.cli.paths import Paths


def get_company_slug() -> str:
    """Return company slug from context."""
    return read_yaml(Paths.context_file())['company_slug']
