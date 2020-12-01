import json
import os

import pytest
from panoramic.cli.config.auth import get_client_id, get_client_secret

_TEST_JWT = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
    'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.'
    'SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
)

from panoramic.cli.context import get_company_slug


@pytest.fixture(autouse=True)
def clear_context_cache():
    get_client_id.cache_clear()
    get_client_secret.cache_clear()
    get_company_slug.cache_clear()
    os.environ.setdefault('PANO_ANALYTICS_ENABLED', 'false')


def scrub_access_token(response):
    """Scrub access token from auth server response."""
    if b'access_token' in response['body']['string']:
        body = json.loads(response['body']['string'])
        body['access_token'] = _TEST_JWT
        response['body']['string'] = json.dumps(body).encode()
    return response


@pytest.fixture(scope='session')
def vcr_config():
    return {'filter_headers': ['authorization'], 'before_record_response': scrub_access_token}
