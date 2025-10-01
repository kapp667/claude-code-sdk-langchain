# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Project Context

This is a **LangChain adapter** for the Claude Code SDK that enables cost-effective prototyping with Claude via a Claude Code subscription (20$/month) instead of direct API costs. The adapter provides behavioral neutrality (~95%) allowing seamless migration from prototyping to production.

**⚠️ CRITICAL MODEL NAME**: Always use `claude-sonnet-4-20250514` as the default model. This has been explicitly confirmed - never change to 3.5, Opus, or other variants.

**Core Value Proposition**: Prototype LangChain applications without API costs, then migrate to `ChatAnthropic` in production by changing one line of code.

## Development Commands

This project uses **Pixi** for dependency management:

```bash
# Development environment
pixi shell                                  # Enter isolated environment

# Testing
pixi run test                              # Run all flow tests (pytest specs/)
pixi run python specs/flow_basic_chat_test.py  # Run specific flow test
pytest specs/flow_streaming_test.py::test_flow_async_chain_streaming_with_parser  # Single test

# Code quality
pixi run format         # Auto-format with black
pixi run lint          # Check with flake8
pixi run typecheck     # Type checking with mypy
pixi run check         # Run all checks

# Cleanup
pixi run clean         # Remove __pycache__, build artifacts
```

## Architecture Overview

### Core Components

**1. ClaudeCodeChatModel** (`src/claude_code_langchain/chat_model.py`)
   - Implements LangChain's `BaseChatModel` interface
   - **Critical async fix**: Uses asyncio.Queue to isolate anyio context from claude-code-sdk, preventing `RuntimeError: Attempted to exit cancel scope in a different task` when using LangChain parsers (`prompt | model | StrOutputParser()`)
   - Sync streaming uses separate event loop in thread for thread-safety
   - Handles temperature/max_tokens with warnings (not supported by CLI)
   - System prompt conflict resolution: SystemMessage takes precedence over constructor param

**2. MessageConverter** (`src/claude_code_langchain/message_converter.py`)
   - Converts LangChain messages ↔ Claude prompt format
   - Detects and warns about multimodal content (images not supported)
   - Extracts usage metadata from ResultMessage
   - **Important**: No escape sequences - passes content verbatim to avoid corruption

### Call Flow

```
LangChain Application (LCEL chains, agents, etc.)
    ↓ LangChain messages (HumanMessage, AIMessage, SystemMessage)
ClaudeCodeChatModel._astream() or ._generate()
    ↓ MessageConverter.langchain_to_claude_prompt()
claude-code-sdk query() function
    ↓ subprocess to Claude Code CLI
Claude Code CLI (@anthropic-ai/claude-code)
    ↓ authenticated request
Claude API (via user's subscription)
```

### Critical Implementation Details

**Async Streaming with Parsers**:
```python
# Problem: anyio task group in SDK conflicts with LangChain's asyncio iterators
# Solution: Queue-based isolation pattern
async def _astream():
    chunk_queue = asyncio.Queue()

    async def consume_sdk_stream():
        # Isolated task consumes SDK stream
        async for message in query(...):
            await chunk_queue.put(chunk)
        await chunk_queue.put(None)  # EOF signal

    consumer_task = asyncio.create_task(consume_sdk_stream())

    while True:
        chunk = await chunk_queue.get()
        if chunk is None: break
        yield chunk
```

This pattern enables `prompt | model | StrOutputParser()` to work correctly.

**Known Limitations** (documented with warnings):
- `temperature` and `max_tokens` parameters accepted for API compatibility but have no effect (CLI doesn't support them)
- Vision/multimodal content not supported (images detected and warned)
- System prompt: if both constructor `system_prompt` and `SystemMessage` provided, SystemMessage takes precedence

## Testing Philosophy

**Pragmatic Flow Testing** (not traditional unit tests):
- Test through public APIs only (`invoke()`, `stream()`, `astream()`)
- Real end-to-end flows with actual Claude CLI
- No mocking - tests validate real behavior
- Flow descriptions in markdown, pytest implementations in parallel files
- Pattern: `specs/flow_name.md` + `specs/flow_name_test.py`

**Current Status**: 16/16 functional tests pass (100%)

**Why this approach**: LLMs naturally perform "unit testing" through code inference. Explicit tests validate user-facing flows, not implementation details.

## Migration Path

**Development (this adapter)**:
```python
from src.claude_code_langchain import ClaudeCodeChatModel
model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514")
```

**Production (official API)**:
```python
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-5-sonnet-20241022", api_key=os.getenv("ANTHROPIC_API_KEY"))
```

Everything else stays identical - this is the core design principle.

## Prerequisites

1. **Claude Code CLI** must be installed and authenticated:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Active Claude Code subscription** (20$/month)

3. **Pixi** for development:
   ```bash
   curl -fsSL https://pixi.sh/install.sh | bash
   ```

## Key Behavioral Differences from Production API

These are intentional trade-offs for the cost-free prototyping model:

1. **No temperature/max_tokens control** - CLI doesn't expose these parameters
2. **No vision/multimodal** - Only text content supported
3. **Higher latency** - Subprocess overhead vs direct API
4. **No tool calls** - Can be simulated via prompting
5. **Subscription quotas** - Limited by Claude Code plan limits

All differences are documented with warnings at runtime.

## Documentation References

- `docs/VALIDATION_REPORT_2025-09-30.md` - Comprehensive 3-agent analysis, bug fixes, neutrality scoring
- `docs/TEMPERATURE_MAX_TOKENS_INVESTIGATION.md` - Deep dive on CLI limitations
- `IMPORTANT_MODEL_NOTE.md` - Model name rationale and history
- `README.md` - User-facing documentation with examples
