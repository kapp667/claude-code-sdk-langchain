"""
LangChain chat model using Claude Code SDK
"""

import asyncio
import logging
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    SystemMessage,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field

logger = logging.getLogger(__name__)

# Import Claude Code SDK avec gestion d'erreurs
try:
    from claude_code_sdk import (
        AssistantMessage,
        ClaudeCodeOptions,
        CLIJSONDecodeError,
        CLINotFoundError,
        ProcessError,
        ResultMessage,
        TextBlock,
        ThinkingBlock,
        query,
    )

    CLAUDE_CODE_AVAILABLE = True
except ImportError as e:
    CLAUDE_CODE_AVAILABLE = False
    logger.error(f"claude-code-sdk not installed: {e}")

from .message_converter import MessageConverter  # noqa: E402


class ClaudeCodeChatModel(BaseChatModel):
    """
    LangChain chat model using Claude via your Claude Code subscription.

    This allows you to use Claude in LangChain WITHOUT additional API costs,
    using your existing Claude Code subscription ($20/month).

    Limitations:
        - temperature: Accepted for API compatibility but NOT supported by Claude Code CLI
        - max_tokens: Accepted for API compatibility but NOT supported by Claude Code CLI

    For applications requiring temperature or token limit control, use ChatAnthropic
    with an Anthropic API key instead.

    Example:
        .. code-block:: python

            model = ClaudeCodeChatModel(
                model="claude-sonnet-4-20250514",
                temperature=0.7,  # WARNING: Not supported, will use default
                max_tokens=1000   # WARNING: Not supported, will use default
            )

            # Simple usage
            response = model.invoke([HumanMessage(content="Hello!")])

            # With streaming
            for chunk in model.stream([HumanMessage(content="Tell me a story")]):
                print(chunk.content, end="")

            # In a LangChain chain
            from langchain.prompts import ChatPromptTemplate

            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an assistant"),
                ("human", "{input}")
            ])

            chain = prompt | model
            result = chain.invoke({"input": "What is LangChain?"})
    """

    model_name: str = Field(default="claude-sonnet-4-20250514", alias="model")
    """Claude model name to use - DO NOT CHANGE (Sonnet 4 confirmed by user)"""

    temperature: Optional[float] = Field(default=0.7)
    """Temperature for generation (0.0 to 1.0) - NOT SUPPORTED by Claude Code CLI"""

    max_tokens: Optional[int] = Field(default=2000)
    """Maximum number of tokens to generate - NOT SUPPORTED by Claude Code CLI"""

    system_prompt: Optional[str] = Field(default=None)
    """Optional system prompt"""

    permission_mode: str = Field(default="default")
    """Claude Code permission mode: default, acceptEdits, plan, bypassPermissions"""  # type: ignore[assignment]

    allowed_tools: List[str] = Field(default_factory=list)
    """List of allowed Claude Code tools"""

    cwd: Optional[str] = Field(default=None)
    """Working directory for Claude Code"""

    _converter: MessageConverter = MessageConverter()
    """Message converter"""

    def __init__(self, **kwargs):
        """Initialize the Claude Code model"""
        super().__init__(**kwargs)

        if not CLAUDE_CODE_AVAILABLE:
            raise ImportError(
                "claude-code-sdk n'est pas installé. "
                "Installez-le avec: pip install claude-code-sdk\n"
                "Et assurez-vous que Claude Code CLI est installé: "
                "npm install -g @anthropic-ai/claude-code"
            )

        # Warning si temperature non-défaut spécifiée
        if self.temperature is not None and self.temperature != 0.7:
            logger.warning(
                f"⚠️  Temperature {self.temperature} NOT SUPPORTED by Claude Code CLI. "
                f"Model will use default temperature. "
                f"For temperature control, use production API (ChatAnthropic). "
                f"See: https://docs.anthropic.com/claude/reference/messages_post"
            )

        # Warning si max_tokens non-défaut spécifié
        if self.max_tokens is not None and self.max_tokens != 2000:
            logger.warning(
                f"⚠️  max_tokens {self.max_tokens} NOT SUPPORTED by Claude Code CLI. "
                f"Model will use default token limit. "
                f"For token limit control, use production API (ChatAnthropic)."
            )

    def _get_claude_options(self, messages: List[BaseMessage]) -> ClaudeCodeOptions:
        """Build options for Claude Code SDK

        Args:
            messages: List of messages to determine if SystemMessage is present

        Returns:
            Configured ClaudeCodeOptions
        """
        # Note: Temperature and max_tokens are NOT supported by Claude CLI
        # These parameters are accepted for API compatibility but have no effect
        # Warnings emitted in __init__ if non-default values

        # Handle system_prompt conflict:
        # If SystemMessage present in messages, don't pass system_prompt via options
        # to avoid having two system prompts (one via options, one via prompt text)
        has_system_message = any(isinstance(msg, SystemMessage) for msg in messages)

        effective_system_prompt = None if has_system_message else self.system_prompt

        if has_system_message and self.system_prompt:
            logger.warning(
                "Both constructor system_prompt and SystemMessage detected. "
                "Using SystemMessage from messages (takes precedence). "
                "Constructor system_prompt will be ignored."
            )

        return ClaudeCodeOptions(
            model=self.model_name,
            system_prompt=effective_system_prompt,
            permission_mode=self.permission_mode,  # type: ignore[arg-type]
            allowed_tools=self.allowed_tools,
            cwd=self.cwd,
            max_turns=1,  # For simple chat behavior
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Synchronous generation using asyncio with enhanced error handling.

        Args:
            messages: Input messages
            stop: Stop sequences (not supported by Claude Code SDK)
            run_manager: Callback manager

        Returns:
            ChatResult with generated response
        """
        # Warn if unsupported stop sequences or kwargs are passed
        if stop:
            logger.warning(
                f"Stop sequences {stop} are not supported by Claude Code SDK and will be ignored. "
                "This may cause different behavior when migrating to production APIs."
            )
        if kwargs:
            logger.warning(
                f"Additional parameters {list(kwargs.keys())} are not supported and will be ignored."
            )

        try:
            # Check if an event loop already exists
            asyncio.get_running_loop()
            # If in a loop, use run_in_executor
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, self._agenerate(messages, stop, None, **kwargs)
                )
                return future.result()
        except RuntimeError:
            # No active loop, can use asyncio.run directly
            return asyncio.run(self._agenerate(messages, stop, None, **kwargs))

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Asynchronous generation via Claude Code SDK with error handling.

        Args:
            messages: Input messages
            stop: Stop sequences (not supported by Claude Code SDK)
            run_manager: Asynchronous callback manager

        Returns:
            ChatResult with generated response
        """
        # Warn if unsupported stop sequences or kwargs are passed
        if stop:
            logger.warning(
                f"Stop sequences {stop} are not supported by Claude Code SDK and will be ignored. "
                "This may cause different behavior when migrating to production APIs."
            )
        if kwargs:
            logger.warning(
                f"Additional parameters {list(kwargs.keys())} are not supported and will be ignored."
            )

        try:
            # Convert LangChain messages to Claude prompt
            prompt = self._converter.langchain_to_claude_prompt(messages)

            # Collect response
            result_content = ""
            thinking_content = ""
            usage_metadata = {}

            # Use query() for simple interaction
            async for message in query(prompt=prompt, options=self._get_claude_options(messages)):
                if isinstance(message, AssistantMessage):
                    # Extract text content and thinking
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            result_content += block.text
                        elif isinstance(block, ThinkingBlock):
                            thinking_content += block.thinking

                elif isinstance(message, ResultMessage):
                    # Extract usage metadata
                    usage_metadata = self._converter.extract_usage_metadata(message)
                    if message.is_error:
                        raise RuntimeError(f"Claude Code error: {message.result}")

            # Create LangChain response message
            # Put thinking in additional_kwargs for consistency with streaming
            additional_kwargs = {"model": self.model_name}
            if thinking_content:
                additional_kwargs["thinking"] = thinking_content

            ai_message = AIMessage(
                content=result_content,
                additional_kwargs=additional_kwargs,
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
                f"Claude Code process error (exit code {e.exit_code}): {e}\n" f"Stderr: {e.stderr}"
            )
        except CLIJSONDecodeError as e:
            raise RuntimeError(
                f"Failed to parse Claude Code response: {e}\n" f"Invalid line: {e.line}"
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
        Synchronous streaming with enhanced error handling.

        Args:
            messages: Input messages
            stop: Stop sequences
            run_manager: Callback manager

        Yields:
            ChatGenerationChunk for each part of the response
        """
        # Use thread-safe approach for sync streaming
        try:
            # Create new event loop in thread with synchronization
            import queue
            import threading

            chunk_queue: queue.Queue = queue.Queue()
            exception_holder = {"exception": None}
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
                            exception_holder["exception"] = e
                        finally:
                            done_event.set()

                    loop.run_until_complete(stream_chunks())
                except Exception as e:
                    exception_holder["exception"] = e
                    done_event.set()
                finally:
                    loop.close()

            # Execute in separate thread (non-daemon for clean cleanup)
            thread = threading.Thread(target=run_async_generator, daemon=False)
            thread.start()

            # Yield chunks in real-time
            while not done_event.is_set() or not chunk_queue.empty():
                try:
                    chunk = chunk_queue.get(timeout=0.1)
                    # ChatGenerationChunk contains an AIMessageChunk in .message
                    # Check content is not None (not just truthiness)
                    if (
                        run_manager
                        and hasattr(chunk, "message")
                        and chunk.message.content is not None
                    ):
                        run_manager.on_llm_new_token(chunk.message.content)
                    # Return complete ChatGenerationChunk for LangChain
                    yield chunk
                except queue.Empty:
                    continue

            # Check exceptions after processing
            if exception_holder["exception"]:
                raise exception_holder["exception"]

            # Wait for thread to complete cleanly (no timeout)
            thread.join()

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
        Asynchronous streaming via Claude Code SDK with ThinkingBlock handling.

        Uses an asyncio queue to isolate the SDK's anyio context and avoid
        cancel scope issues with LangChain parsers.

        Args:
            messages: Input messages
            stop: Stop sequences
            run_manager: Asynchronous callback manager

        Yields:
            ChatGenerationChunk for each part of the response
        """
        # Create queue to transfer chunks between tasks
        chunk_queue: asyncio.Queue = asyncio.Queue()
        exception_holder = {"exception": None}

        async def consume_sdk_stream():
            """
            Dedicated task that consumes SDK stream in its own anyio context.
            This isolates the SDK's anyio task group from other LangChain tasks.
            """
            try:
                # Convert messages to prompt
                prompt = self._converter.langchain_to_claude_prompt(messages)

                # Stream response - this async loop executes in isolated task
                async for message in query(
                    prompt=prompt, options=self._get_claude_options(messages)
                ):
                    if isinstance(message, ResultMessage):
                        # Check for errors
                        if message.is_error:
                            raise RuntimeError(f"Claude Code error: {message.result}")

                    elif isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                # Create chunk for each text block
                                chunk = ChatGenerationChunk(
                                    message=AIMessageChunk(content=block.text)
                                )
                                await chunk_queue.put(chunk)

                            elif isinstance(block, ThinkingBlock):
                                # Optional: include thinking in metadata
                                chunk = ChatGenerationChunk(
                                    message=AIMessageChunk(
                                        content="", additional_kwargs={"thinking": block.thinking}
                                    )
                                )
                                await chunk_queue.put(chunk)

                # End signal
                await chunk_queue.put(None)

            except Exception as e:
                exception_holder["exception"] = e
                await chunk_queue.put(None)

        # Launch SDK consumption task in isolated context
        consumer_task = asyncio.create_task(consume_sdk_stream())

        try:
            # Yield chunks from queue
            while True:
                chunk = await chunk_queue.get()

                # Check consumer task exception
                if exception_holder["exception"]:
                    raise exception_holder["exception"]

                # None = end of stream
                if chunk is None:
                    break

                # Callback manager
                if run_manager and chunk.message.content:
                    await run_manager.on_llm_new_token(chunk.message.content)

                yield chunk

        except Exception as e:
            logger.error(f"Error in async streaming: {e}")
            # Cancel consumer task if error
            consumer_task.cancel()
            raise

        finally:
            # Ensure consumer task is completed
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass

    @property
    def _llm_type(self) -> str:
        """LLM type for identification"""
        return "claude-code"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Identifying parameters for tracing"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "permission_mode": self.permission_mode,
        }

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Default model parameters"""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
