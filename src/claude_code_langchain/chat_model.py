"""
Modèle de chat LangChain utilisant Claude Code SDK
"""

import asyncio
from typing import (
    Any, Dict, Iterator, List, Optional, AsyncIterator,
    Mapping, Union
)

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field
import logging

logger = logging.getLogger(__name__)

# Import Claude Code SDK avec gestion d'erreurs
try:
    from claude_code_sdk import (
        query,
        ClaudeSDKClient,
        ClaudeCodeOptions,
        AssistantMessage,
        TextBlock,
        ThinkingBlock,
        ResultMessage,
        CLINotFoundError,
        ProcessError,
        CLIJSONDecodeError,
    )
    CLAUDE_CODE_AVAILABLE = True
except ImportError as e:
    CLAUDE_CODE_AVAILABLE = False
    logger.error(f"claude-code-sdk not installed: {e}")

from .message_converter import MessageConverter


class ClaudeCodeChatModel(BaseChatModel):
    """
    Modèle de chat LangChain utilisant Claude via votre abonnement Claude Code.

    Cela vous permet d'utiliser Claude dans LangChain SANS frais API supplémentaires,
    en utilisant votre abonnement Claude Code existant (20$/mois).

    Example:
        .. code-block:: python

            model = ClaudeCodeChatModel(
                model="claude-3-5-sonnet-20241022",
                temperature=0.7,
                max_tokens=1000
            )

            # Utilisation simple
            response = model.invoke([HumanMessage(content="Bonjour!")])

            # Avec streaming
            for chunk in model.stream([HumanMessage(content="Raconte une histoire")]):
                print(chunk.content, end="")

            # Dans une chaîne LangChain
            from langchain.prompts import ChatPromptTemplate

            prompt = ChatPromptTemplate.from_messages([
                ("system", "Tu es un assistant"),
                ("human", "{input}")
            ])

            chain = prompt | model
            result = chain.invoke({"input": "Qu'est-ce que LangChain?"})
    """

    model_name: str = Field(default="claude-sonnet-4-20250514", alias="model")
    """Nom du modèle Claude à utiliser - NE PAS CHANGER (Sonnet 4 confirmé par l'utilisateur)"""

    temperature: Optional[float] = Field(default=0.7)
    """Température pour la génération (0.0 à 1.0)"""

    max_tokens: Optional[int] = Field(default=2000)
    """Nombre maximum de tokens à générer"""

    system_prompt: Optional[str] = Field(default=None)
    """Prompt système optionnel"""

    permission_mode: str = Field(default="default")
    """Mode de permission Claude Code: default, acceptEdits, plan, bypassPermissions"""

    allowed_tools: List[str] = Field(default_factory=list)
    """Liste des outils Claude Code autorisés"""

    cwd: Optional[str] = Field(default=None)
    """Répertoire de travail pour Claude Code"""

    use_continuous_session: bool = Field(default=False)
    """Si True, maintient une session continue avec mémoire"""

    _client: Optional[ClaudeSDKClient] = None
    """Client SDK pour les sessions continues"""

    _converter: MessageConverter = MessageConverter()
    """Convertisseur de messages"""

    def __init__(self, **kwargs):
        """Initialise le modèle Claude Code"""
        super().__init__(**kwargs)

        if not CLAUDE_CODE_AVAILABLE:
            raise ImportError(
                "claude-code-sdk n'est pas installé. "
                "Installez-le avec: pip install claude-code-sdk\n"
                "Et assurez-vous que Claude Code CLI est installé: "
                "npm install -g @anthropic-ai/claude-code"
            )

        # Initialiser le client si mode session continue
        if self.use_continuous_session:
            self._client = ClaudeSDKClient(options=self._get_claude_options())

    def _get_claude_options(self) -> ClaudeCodeOptions:
        """Construit les options pour Claude Code SDK"""
        return ClaudeCodeOptions(
            model=self.model_name,
            system_prompt=self.system_prompt,
            permission_mode=self.permission_mode,
            allowed_tools=self.allowed_tools,
            cwd=self.cwd,
            max_turns=1,  # Pour comportement chat simple
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Génération synchrone utilisant asyncio avec gestion d'erreurs améliorée.

        Args:
            messages: Messages d'entrée
            stop: Séquences d'arrêt
            run_manager: Gestionnaire de callbacks

        Returns:
            ChatResult avec la réponse générée
        """
        try:
            # Vérifier si une boucle d'événements existe déjà
            loop = asyncio.get_running_loop()
            # Si on est dans une boucle, utiliser run_in_executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self._agenerate(messages, stop, None, **kwargs)
                )
                return future.result()
        except RuntimeError:
            # Pas de boucle active, on peut utiliser asyncio.run directement
            return asyncio.run(
                self._agenerate(messages, stop, None, **kwargs)
            )

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Génération asynchrone via Claude Code SDK avec gestion d'erreurs.

        Args:
            messages: Messages d'entrée
            stop: Séquences d'arrêt
            run_manager: Gestionnaire de callbacks asynchrone

        Returns:
            ChatResult avec la réponse générée
        """
        try:
            # Convertir les messages LangChain en prompt pour Claude
            prompt = self._converter.langchain_to_claude_prompt(messages)

            # Collecter la réponse
            result_content = ""
            thinking_content = ""
            usage_metadata = {}

            # Utiliser query() pour une interaction simple
            async for message in query(prompt=prompt, options=self._get_claude_options()):
                if isinstance(message, AssistantMessage):
                    # Extraire le contenu textuel et thinking
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            result_content += block.text
                        elif isinstance(block, ThinkingBlock):
                            thinking_content += block.thinking

                elif isinstance(message, ResultMessage):
                    # Extraire les métadonnées d'usage
                    usage_metadata = self._converter.extract_usage_metadata(message)
                    if message.is_error:
                        raise RuntimeError(f"Claude Code error: {message.result}")

            # Ajouter le thinking au metadata si présent
            if thinking_content:
                usage_metadata["thinking"] = thinking_content

            # Créer le message de réponse LangChain
            ai_message = AIMessage(
                content=result_content,
                additional_kwargs={"model": self.model_name},
                response_metadata=usage_metadata,
            )

            generation = ChatGeneration(message=ai_message)
            return ChatResult(generations=[generation])

        except CLINotFoundError as e:
            raise RuntimeError(
                f"Claude Code CLI not found: {e}\n"
                "Please install: npm install -g @anthropic-ai/claude-code"
            )
        except ProcessError as e:
            raise RuntimeError(
                f"Claude Code process error (exit code {e.exit_code}): {e}\n"
                f"Stderr: {e.stderr}"
            )
        except CLIJSONDecodeError as e:
            raise RuntimeError(
                f"Failed to parse Claude Code response: {e}\n"
                f"Invalid line: {e.line}"
            )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """
        Streaming synchrone avec gestion d'erreurs améliorée.

        Args:
            messages: Messages d'entrée
            stop: Séquences d'arrêt
            run_manager: Gestionnaire de callbacks

        Yields:
            ChatGenerationChunk pour chaque partie de la réponse
        """
        # Utiliser une approche thread-safe pour le streaming sync
        try:
            # Créer une nouvelle boucle d'événements dans un thread avec synchronisation
            import concurrent.futures
            import threading
            import queue

            chunk_queue = queue.Queue()
            exception_holder = {'exception': None}
            done_event = threading.Event()

            def run_async_generator():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    async def stream_chunks():
                        try:
                            async for chunk in self._astream(messages, stop, None, **kwargs):
                                chunk_queue.put(chunk)
                        except Exception as e:
                            exception_holder['exception'] = e
                        finally:
                            done_event.set()

                    loop.run_until_complete(stream_chunks())
                except Exception as e:
                    exception_holder['exception'] = e
                    done_event.set()
                finally:
                    loop.close()

            # Exécuter dans un thread séparé
            thread = threading.Thread(target=run_async_generator, daemon=True)
            thread.start()

            # Yielder les chunks en temps réel
            while not done_event.is_set() or not chunk_queue.empty():
                try:
                    chunk = chunk_queue.get(timeout=0.1)
                    if run_manager and chunk.message.content:
                        run_manager.on_llm_new_token(chunk.message.content)
                    yield chunk
                except queue.Empty:
                    continue

            # Vérifier les exceptions après traitement
            if exception_holder['exception']:
                raise exception_holder['exception']

            thread.join(timeout=1.0)

        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            raise

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """
        Streaming asynchrone via Claude Code SDK avec gestion des ThinkingBlock.

        Args:
            messages: Messages d'entrée
            stop: Séquences d'arrêt
            run_manager: Gestionnaire de callbacks asynchrone

        Yields:
            ChatGenerationChunk pour chaque partie de la réponse
        """
        try:
            # Convertir les messages en prompt
            prompt = self._converter.langchain_to_claude_prompt(messages)

            # Stream la réponse
            async for message in query(prompt=prompt, options=self._get_claude_options()):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Créer un chunk pour chaque bloc de texte
                            chunk = ChatGenerationChunk(
                                message=AIMessageChunk(content=block.text)
                            )

                            if run_manager:
                                await run_manager.on_llm_new_token(block.text)

                            yield chunk

                        elif isinstance(block, ThinkingBlock):
                            # Optionnel: inclure le thinking dans les métadonnées
                            chunk = ChatGenerationChunk(
                                message=AIMessageChunk(
                                    content="",
                                    additional_kwargs={"thinking": block.thinking}
                                )
                            )
                            yield chunk

        except Exception as e:
            logger.error(f"Error in async streaming: {e}")
            raise

    async def aconnect(self) -> None:
        """
        Connecte le client pour les sessions continues.
        Utilisé uniquement si use_continuous_session=True.
        """
        if self.use_continuous_session and self._client:
            try:
                await self._client.connect()
            except Exception as e:
                logger.error(f"Failed to connect client: {e}")
                raise

    async def adisconnect(self) -> None:
        """
        Déconnecte le client pour les sessions continues.
        """
        if self.use_continuous_session and self._client:
            try:
                await self._client.disconnect()
            except Exception as e:
                logger.error(f"Failed to disconnect client: {e}")

    async def __aenter__(self):
        """Support du context manager async"""
        if self.use_continuous_session:
            await self.aconnect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Sortie du context manager async"""
        if self.use_continuous_session:
            await self.adisconnect()

    @property
    def _llm_type(self) -> str:
        """Type de LLM pour identification"""
        return "claude-code"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Paramètres d'identification pour le tracing"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "permission_mode": self.permission_mode,
            "use_continuous_session": self.use_continuous_session,
        }

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Paramètres par défaut du modèle"""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }