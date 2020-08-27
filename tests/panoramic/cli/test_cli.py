from unittest.mock import Mock, patch

import pytest
from click.core import Context

from panoramic.cli.cli import (
    ConfigAwareCommand,
    ContextAwareCommand,
    LocalStateAwareCommand,
)
from panoramic.cli.errors import ValidationError


@patch('panoramic.cli.validate.validate_config')
@patch('panoramic.cli.validate.validate_context', side_effect=ValidationError('test'))
def test_context_aware_command_invalid(_, __):
    """Check command fails when no context."""
    with pytest.raises(SystemExit):
        ContextAwareCommand(name='test-command').invoke(Mock())


@patch('panoramic.cli.validate.validate_config')
@patch('panoramic.cli.validate.validate_context')
def test_context_aware_command_valid(_, __):
    """Check command succeeds when context exists."""

    def test_callback():
        return 10

    command = ContextAwareCommand(name='test-command', callback=test_callback)
    context = Context(command)

    assert command.invoke(context) == 10


@patch('panoramic.cli.validate.validate_config', side_effect=ValidationError('test'))
def test_config_aware_command_invalid(_):
    """Check command fails when no context."""
    with pytest.raises(SystemExit):
        ConfigAwareCommand(name='test-command').invoke(Mock())


@patch('panoramic.cli.validate.validate_config')
def test_config_aware_command_config_exists(_):
    """Check command succeeds when context exists."""

    def test_callback():
        return 10

    command = ConfigAwareCommand(name='test-command', callback=test_callback)
    context = Context(command)

    assert command.invoke(context) == 10


@patch('panoramic.cli.validate.validate_config')
@patch('panoramic.cli.validate.validate_context')
@patch('panoramic.cli.validate.validate_local_state', return_value=[ValidationError('test')])
def test_local_state_aware_command_invalid(_, __, ___):
    """Check command fails when no context."""
    with pytest.raises(SystemExit):
        LocalStateAwareCommand(name='test-command').invoke(Mock())


@patch('panoramic.cli.validate.validate_config')
@patch('panoramic.cli.validate.validate_context')
@patch('panoramic.cli.validate.validate_local_state')
def test_local_state_aware_command_valid(_, __, ___):
    """Check command succeeds when context exists."""

    def test_callback():
        return 10

    command = ConfigAwareCommand(name='test-command', callback=test_callback)
    context = Context(command)

    assert command.invoke(context) == 10
