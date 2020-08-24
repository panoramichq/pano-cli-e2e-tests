from unittest.mock import Mock

import pytest
import yaml
from click.core import Context

from panoramic.cli.cli import ConfigAwareCommand, ContextAwareCommand
from panoramic.cli.paths import Paths


def test_context_aware_command_no_context(monkeypatch, tmpdir):
    """Check command fails when no context."""
    monkeypatch.chdir(tmpdir)
    with pytest.raises(SystemExit):
        ContextAwareCommand(name='test-command').invoke(Mock())

    # TODO: check that correct exception was raised


def test_context_aware_command_context_exists(monkeypatch, tmpdir):
    """Check command succeeds when context exists."""
    monkeypatch.chdir(tmpdir)

    with Paths.context_file().open('w+') as f:
        f.write(yaml.dump({'company_slug': 'test-company', 'api_version': 'v1'}))

    def test_callback():
        return 10

    command = ContextAwareCommand(name='test-command', callback=test_callback)
    context = Context(command)

    assert command.invoke(context) == 10


def test_config_aware_command_no_config(monkeypatch, tmpdir):
    """Check command fails when no context."""
    monkeypatch.setenv('HOME', tmpdir)

    with pytest.raises(SystemExit):
        ConfigAwareCommand(name='test-command').invoke(Mock())

    # TODO: check that correct exception was raised


def test_config_aware_command_config_exists(monkeypatch, tmpdir):
    """Check command succeeds when context exists."""
    monkeypatch.setenv('HOME', tmpdir)

    Paths.config_dir().mkdir()
    with Paths.config_file().open('w+') as f:
        f.write(yaml.dump({'client_id': 'test-client-id', 'client_secret': 'test-client-secret', 'api_version': 'v1'}))

    def test_callback():
        return 10

    command = ContextAwareCommand(name='test-command', callback=test_callback)
    context = Context(command)

    assert command.invoke(context) == 10
