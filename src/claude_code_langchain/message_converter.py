"""
Message converter between LangChain and Claude Code SDK
"""

import logging
from typing import Any, Dict, List

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

logger = logging.getLogger(__name__)


class MessageConverter:
    """Converts between LangChain and Claude Code message formats"""

    @staticmethod
    def langchain_to_claude_prompt(messages: List[BaseMessage]) -> str:
        """
        Converts a list of LangChain messages to a prompt string for Claude Code.

        Args:
            messages: List of LangChain messages

        Returns:
            Formatted prompt for Claude Code SDK

        Raises:
            ValueError: If message list is empty or contains invalid messages
        """
        if not messages:
            raise ValueError("Message list cannot be empty")

        prompt_parts = []

        for i, message in enumerate(messages):
            # Content validation
            if message.content is None:
                logger.warning(f"Message {i} has None content, ignored")
                continue

            # Handle different content types
            if isinstance(message.content, str):
                content = message.content.strip()
            elif isinstance(message.content, list):
                # Multimodal content (text + images)
                content_parts = []

                for part in message.content:
                    if isinstance(part, dict):
                        # Check content type
                        part_type = part.get("type", "")

                        if part_type in ["image_url", "image"] or "image_url" in part:
                            # Image detected - not supported
                            logger.warning(
                                f"Image content detected in message {i} but NOT SUPPORTED by Claude Code SDK. "
                                "Image will be ignored. This differs from production API behavior "
                                "(ChatAnthropic supports vision). Consider using production API for vision tasks."
                            )
                        elif "text" in part:
                            content_parts.append(part["text"])
                        else:
                            # Other non-text content type
                            if part_type and part_type != "text":
                                logger.warning(
                                    f"Non-text content type '{part_type}' detected in message {i} and will be ignored. "
                                    "Only text content is supported by Claude Code SDK."
                                )
                    elif isinstance(part, str):
                        content_parts.append(part)

                content = " ".join(content_parts).strip()
            else:
                content = str(message.content).strip()

            if not content:
                logger.warning(f"Message {i} has empty content, ignored")
                continue

            if isinstance(message, SystemMessage):
                # System messages become context
                prompt_parts.append(f"System: {content}")

            elif isinstance(message, HumanMessage):
                prompt_parts.append(f"Human: {content}")

            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {content}")

            elif isinstance(message, (ToolMessage, FunctionMessage)):
                # Tool messages are specially formatted
                prompt_parts.append(f"Tool Result: {content}")

            else:
                # Fallback for any other type
                prompt_parts.append(content)

        if not prompt_parts:
            raise ValueError("No valid message to convert")

        # Claude Code SDK expects simple or structured prompt
        return "\n\n".join(prompt_parts)

    @staticmethod
    def langchain_to_claude_dict(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """
        Converts LangChain messages to dict format for streaming.

        Args:
            messages: List of LangChain messages

        Returns:
            List of dicts for Claude Code SDK streaming
        """
        result = []

        for message in messages:
            if isinstance(message, SystemMessage):
                # Add as system context
                result.append({"type": "text", "text": f"[System Instructions]\n{message.content}"})

            elif isinstance(message, HumanMessage):
                result.append({"type": "text", "text": str(message.content)})

            elif isinstance(message, AIMessage):
                # To maintain conversation context
                result.append(
                    {"type": "text", "text": f"[Previous Assistant Response]\n{message.content}"}
                )

            elif isinstance(message, (ToolMessage, FunctionMessage)):
                result.append({"type": "text", "text": f"[Tool Output]\n{message.content}"})

        return result

    @staticmethod
    def extract_content_from_claude(claude_message) -> str:
        """
        Extracts text content from a Claude Code message.

        Args:
            claude_message: Message from Claude Code SDK

        Returns:
            Extracted text content
        """
        from claude_code_sdk import AssistantMessage, TextBlock

        content = ""

        if isinstance(claude_message, AssistantMessage):
            for block in claude_message.content:
                if isinstance(block, TextBlock):
                    content += block.text

        return content

    @staticmethod
    def extract_usage_metadata(claude_message) -> Dict[str, Any]:
        """
        Extracts usage metadata from a Claude Code message with error handling.

        Args:
            claude_message: Message from Claude Code SDK

        Returns:
            Dictionary of usage metadata
        """
        from claude_code_sdk import ResultMessage

        metadata: Dict[str, Any] = {}

        try:
            if isinstance(claude_message, ResultMessage):
                # Safe extraction with validation
                if hasattr(claude_message, "usage") and claude_message.usage:
                    metadata["usage"] = claude_message.usage

                if (
                    hasattr(claude_message, "total_cost_usd")
                    and claude_message.total_cost_usd is not None
                ):
                    metadata["cost_usd"] = float(claude_message.total_cost_usd)

                if (
                    hasattr(claude_message, "duration_ms")
                    and claude_message.duration_ms is not None
                ):
                    metadata["duration_ms"] = int(claude_message.duration_ms)

                if hasattr(claude_message, "session_id") and claude_message.session_id:
                    metadata["session_id"] = str(claude_message.session_id)

        except (AttributeError, TypeError, ValueError) as e:
            logger.warning(f"Error extracting metadata: {e}")

        return metadata
