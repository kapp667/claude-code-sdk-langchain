"""Claude Code SDK for LangChain integration."""

__version__ = "0.1.0"
__author__ = "Stéphane Wootha Richard"

from .client import ClaudeSDKClient
from .query import query

__all__ = ["ClaudeSDKClient", "query"]