"""
Convertisseur de messages entre LangChain et Claude Code SDK
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
    """Convertit entre les formats de messages LangChain et Claude Code"""

    @staticmethod
    def langchain_to_claude_prompt(messages: List[BaseMessage]) -> str:
        """
        Convertit une liste de messages LangChain en prompt string pour Claude Code.

        Args:
            messages: Liste de messages LangChain

        Returns:
            Prompt formaté pour Claude Code SDK

        Raises:
            ValueError: Si la liste de messages est vide ou contient des messages invalides
        """
        if not messages:
            raise ValueError("La liste de messages ne peut pas être vide")

        prompt_parts = []

        for i, message in enumerate(messages):
            # Validation du contenu
            if message.content is None:
                logger.warning(f"Message {i} a un contenu None, ignoré")
                continue

            # Gérer les différents types de contenu
            if isinstance(message.content, str):
                content = message.content.strip()
            elif isinstance(message.content, list):
                # Contenu multimodal (texte + images)
                content_parts = []

                for part in message.content:
                    if isinstance(part, dict):
                        # Vérifier le type de contenu
                        part_type = part.get("type", "")

                        if part_type in ["image_url", "image"] or "image_url" in part:
                            # Image détectée - non supportée
                            logger.warning(
                                f"Image content detected in message {i} but NOT SUPPORTED by Claude Code SDK. "
                                "Image will be ignored. This differs from production API behavior "
                                "(ChatAnthropic supports vision). Consider using production API for vision tasks."
                            )
                        elif "text" in part:
                            content_parts.append(part["text"])
                        else:
                            # Autre type de contenu non-text
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
                logger.warning(f"Message {i} a un contenu vide, ignoré")
                continue

            if isinstance(message, SystemMessage):
                # Les messages système deviennent du contexte
                prompt_parts.append(f"System: {content}")

            elif isinstance(message, HumanMessage):
                prompt_parts.append(f"Human: {content}")

            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {content}")

            elif isinstance(message, (ToolMessage, FunctionMessage)):
                # Les messages d'outils sont formatés spécialement
                prompt_parts.append(f"Tool Result: {content}")

            else:
                # Fallback pour tout autre type
                prompt_parts.append(content)

        if not prompt_parts:
            raise ValueError("Aucun message valide à convertir")

        # Claude Code SDK attend un prompt simple ou structuré
        return "\n\n".join(prompt_parts)

    @staticmethod
    def langchain_to_claude_dict(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """
        Convertit les messages LangChain en format dict pour streaming.

        Args:
            messages: Liste de messages LangChain

        Returns:
            Liste de dicts pour Claude Code SDK streaming
        """
        result = []

        for message in messages:
            if isinstance(message, SystemMessage):
                # Ajouter comme contexte système
                result.append({"type": "text", "text": f"[System Instructions]\n{message.content}"})

            elif isinstance(message, HumanMessage):
                result.append({"type": "text", "text": str(message.content)})

            elif isinstance(message, AIMessage):
                # Pour maintenir le contexte de conversation
                result.append(
                    {"type": "text", "text": f"[Previous Assistant Response]\n{message.content}"}
                )

            elif isinstance(message, (ToolMessage, FunctionMessage)):
                result.append({"type": "text", "text": f"[Tool Output]\n{message.content}"})

        return result

    @staticmethod
    def extract_content_from_claude(claude_message) -> str:
        """
        Extrait le contenu textuel d'un message Claude Code.

        Args:
            claude_message: Message du SDK Claude Code

        Returns:
            Contenu textuel extrait
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
        Extrait les métadonnées d'usage d'un message Claude Code avec gestion d'erreurs.

        Args:
            claude_message: Message du SDK Claude Code

        Returns:
            Dictionnaire des métadonnées d'usage
        """
        from claude_code_sdk import ResultMessage

        metadata: Dict[str, Any] = {}

        try:
            if isinstance(claude_message, ResultMessage):
                # Extraction sûre avec validation
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
            logger.warning(f"Erreur lors de l'extraction des métadonnées: {e}")

        return metadata
