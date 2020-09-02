import json

import pytest

_TEST_JWT = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
    'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.'
    'SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
)


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
