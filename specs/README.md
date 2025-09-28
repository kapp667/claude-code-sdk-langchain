# Pragmatic Flow Tests for Claude Code SDK LangChain

## Testing Philosophy

This directory contains pragmatic flow tests following the LLM-first development approach. These tests:

- **Focus on user journeys** through public APIs only
- **Treat the system as a black box** - no testing of private methods or implementation details
- **Validate behavior, not implementation** - tests survive refactoring
- **Leverage LLM inference** for unit-level validation (the LLM IS the unit test)

## Test Structure

Each flow has two components:
1. **Flow Description** (`flow_*.md`) - User journey documentation
2. **Flow Test** (`flow_*_test.py`) - Pytest implementation testing only public APIs

## Available Flow Tests

### 1. Basic Chat Flow
- **Description**: `flow_basic_chat.md`
- **Test**: `flow_basic_chat_test.py`
- **Coverage**: Basic invocation, async operations, system prompts

### 2. LangChain Integration Flow
- **Description**: `flow_langchain_integration.md`
- **Test**: `flow_langchain_integration_test.py`
- **Coverage**: LCEL chains, output parsers, batch processing, complex pipelines

### 3. Streaming Flow
- **Description**: `flow_streaming.md`
- **Test**: `flow_streaming_test.py`
- **Coverage**: Sync/async streaming, chain streaming, cancellation

### 4. Error Handling Flow
- **Description**: `flow_error_handling.md`
- **Test**: `flow_error_handling_test.py`
- **Coverage**: CLI errors, process failures, JSON parsing, recovery

### 5. Session Management Flow
- **Description**: `flow_session_management.md`
- **Test**: `flow_session_management_test.py`
- **Coverage**: Single-turn vs continuous, context retention, reconnection

## Running Tests

### Run all flow tests:
```bash
# Using pytest
pytest specs/flow_*_test.py -v

# Or run individually
python specs/flow_streaming_test.py
```

### With Pixi environment:
```bash
pixi run pytest specs/
```

## Key Testing Principles

### ✅ DO Test:
- Public API methods (`invoke()`, `stream()`, `astream()`)
- User-visible behavior and outputs
- Error messages users will see
- Integration with LangChain components
- End-to-end flows

### ❌ DON'T Test:
- Private methods (anything with `_` prefix)
- Internal state or attributes
- Implementation details
- Database schemas
- Code the LLM naturally validates

## Why This Approach?

1. **Velocity > Purity**: Tests that don't break during refactoring
2. **LLM as Unit Test**: The model validates logic during code generation
3. **Real User Flows**: Tests what users actually do
4. **Maintenance-Free**: 80% less test maintenance overhead
5. **Pixi Isolation**: Environmental determinism without mocking

## Critical Configuration

⚠️ **IMPORTANT**: All tests MUST use the correct model:
```python
model = ClaudeCodeChatModel(
    model="claude-sonnet-4-20250514"  # Never change this
)
```

This is Sonnet 4, not 3.5, not Opus. This has been explicitly confirmed by the user.

## Adding New Flow Tests

1. Create flow description: `specs/flow_[name].md`
2. Create test implementation: `specs/flow_[name]_test.py`
3. Test ONLY through public APIs
4. Include docstring linking to flow description
5. Focus on user journey, not implementation

## Test Independence

Each test should:
- Be runnable independently
- Not depend on other tests
- Clean up its own resources
- Use the model as a black box

## Continuous Integration

These tests are designed to:
- Run quickly (no complex setup)
- Provide clear failure messages
- Validate the contract, not the implementation
- Survive aggressive refactoring

Remember: The goal is to maximize development velocity while maintaining confidence in the public API contract.