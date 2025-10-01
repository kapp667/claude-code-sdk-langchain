"""
Test helpers for flow tests

Provides utilities for creating test models with appropriate settings
"""

import os


def get_test_model_name() -> str:
    """
    Get the model name to use for tests.

    Returns haiku for fast tests, or the value of CLAUDE_TEST_MODEL env var.
    Default to sonnet-4 if not set.

    Usage:
        model = ClaudeCodeChatModel(model=get_test_model_name())
    """
    return os.environ.get("CLAUDE_TEST_MODEL", "claude-sonnet-4-20250514")


def get_test_model_kwargs() -> dict:
    """
    Get standard kwargs for test models.

    Returns a dict with model name and reasonable test parameters.

    Usage:
        model = ClaudeCodeChatModel(**get_test_model_kwargs())
    """
    return {
        "model": get_test_model_name(),
        "temperature": 0.7,
        "max_tokens": 500,
    }
