"""
Claude Code LangChain Adapter

Permet d'utiliser Claude via votre abonnement Claude Code
comme modèle LLM dans LangChain pour le prototypage.
"""

from .chat_model import ClaudeCodeChatModel
from .message_converter import MessageConverter

__all__ = [
    "ClaudeCodeChatModel",
    "MessageConverter",
]

__version__ = "0.1.0"