# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Project Context

This is a LangChain adapter that allows using Claude via Claude Code subscription (20$/month) instead of API costs. The adapter bridges `claude-code-sdk` (Python SDK) with LangChain's `BaseChatModel` interface.

**⚠️ CRITICAL MODEL NAME**: Always use `claude-sonnet-4-20250514` as the default model. Never regress to 3.5 or change to Opus. This has been explicitly confirmed and documented in `IMPORTANT_MODEL_NOTE.md`.

## Development Commands

This project uses **Pixi** for dependency management (not pip/venv):

```bash
# Enter development environment
pixi shell

# Run all tests
pixi run test

# Run specific flow test
pixi run python specs/flow_streaming_test.py

# Linting and formatting
pixi run lint           # Check code style
pixi run format         # Auto-format code
pixi run typecheck      # Type checking
pixi run check          # Run all checks (format, lint, typecheck)

# Run simple validation test
pixi run python test_simple.py

# Clean build artifacts
pixi run clean
```

## Architecture Overview

### Core Components

1. **ClaudeCodeChatModel** (`src/claude_code_langchain/chat_model.py`)
   - Implements LangChain's `BaseChatModel` abstract class
   - Bridges between LangChain message format and Claude Code SDK
   - Handles sync/async invocation and streaming
   - Critical: Uses `query()` from claude-code-sdk for stateless interactions
   - Thread-safe sync streaming implementation using separate event loops

2. **MessageConverter** (`src/claude_code_langchain/message_converter.py`)
   - Converts between LangChain messages (SystemMessage, HumanMessage, AIMessage) and Claude prompt format
   - Extracts usage metadata from Claude responses
   - Handles tool messages and thinking blocks

### Call Flow

```
LangChain Application
    ↓ (LangChain messages)
ClaudeCodeChatModel
    ↓ (converts via MessageConverter)
claude-code-sdk Python SDK
    ↓ (subprocess communication)
Claude Code CLI (@anthropic-ai/claude-code)
    ↓ (authenticated request)
Claude API (via user's subscription)
```

### Key Implementation Details

- **Event Loop Management**: The sync `_generate()` method carefully handles existing event loops to avoid RuntimeError
- **Error Handling**: Specific handling for `CLINotFoundError`, `ProcessError`, and `CLIJSONDecodeError` from the SDK
- **Streaming**: Both sync and async streaming supported, with ThinkingBlock content captured in metadata
- **Session Management**: Optional continuous sessions via `use_continuous_session` flag (uses ClaudeSDKClient)

## Testing Philosophy

Tests follow the **Pragmatic Flow Testing** approach (see `specs/README.md`):
- Test ONLY through public APIs (`invoke()`, `stream()`, `astream()`)
- No mocking or isolation - real end-to-end flows
- Each flow has a markdown description and pytest implementation
- The LLM acts as unit test through inference during code generation

## Migration Path

Development with this adapter:
```python
from src.claude_code_langchain import ClaudeCodeChatModel
model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514")
```

Production with official API:
```python
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-opus-20240229", api_key="sk-...")
```

The rest of the code remains identical - this is a drop-in replacement for prototyping.

## Prerequisites

1. **Claude Code CLI** must be installed:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Active Claude Code subscription** (20$/month)

3. **Pixi package manager** for development

## Known Limitations

- No native tool call support (can be added via prompting)
- Higher latency than direct API due to CLI subprocess overhead
- Limited by Claude Code subscription quotas
- ThinkingBlocks are captured but shown in metadata, not main content