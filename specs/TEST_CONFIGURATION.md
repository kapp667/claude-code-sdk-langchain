# Test Configuration Guide

## Model Selection for Tests

Flow tests make real API calls to Claude which can be slow and expensive. You can configure which model to use for tests.

### Quick Start

**Use Haiku for fast tests** (recommended for CI/development):
```bash
export CLAUDE_TEST_MODEL="haiku"
pixi run test
```

**Use Sonnet for thorough validation**:
```bash
export CLAUDE_TEST_MODEL="sonnet"
pixi run test
```

**Use specific model version**:
```bash
export CLAUDE_TEST_MODEL="claude-sonnet-4-20250514"
pixi run test
```

### Pixi Configuration

The `pixi.toml` file sets `CLAUDE_TEST_MODEL=haiku` by default when you use `pixi shell` or `pixi run`.

You can override this:
```bash
# Temporarily use sonnet
CLAUDE_TEST_MODEL=sonnet pixi run test

# Or edit pixi.toml [activation.env] section
```

### Available Models

Claude Code CLI supports model aliases:
- `haiku` - Fast and cheap (recommended for tests)
- `sonnet` - Balanced performance
- `opus` - Most capable but slowest

Or use full model names:
- `claude-3-5-haiku-20241022`
- `claude-sonnet-4-20250514`
- `claude-3-opus-20240229`

### Implementation

Tests use the helper function from `specs/test_helpers.py`:

```python
from .test_helpers import get_test_model_name

# In your test
model = ClaudeCodeChatModel(model=get_test_model_name())
```

This reads `CLAUDE_TEST_MODEL` environment variable and falls back to the production default if not set.

### Performance Comparison

Approximate response times (for simple queries):
- **Haiku**: 1-2 seconds ⚡️
- **Sonnet**: 3-5 seconds
- **Opus**: 5-10 seconds

For test suites with 20+ API calls, using Haiku can reduce test time from 2+ minutes to under 30 seconds.

### Best Practices

1. **CI/CD**: Always use `haiku` for continuous integration
2. **Pre-deployment**: Run once with `sonnet` to validate quality
3. **Development**: Use `haiku` for quick iteration
4. **Production code**: Keep production default as `claude-sonnet-4-20250514`

### Example Usage

```bash
# Fast development cycle
pixi shell
# (haiku is now default)
pytest specs/flow_basic_chat_test.py

# Thorough validation before deployment
CLAUDE_TEST_MODEL=sonnet pixi run test

# Test a specific model version
CLAUDE_TEST_MODEL=claude-3-5-haiku-20241022 pytest specs/
```

## Why This Approach?

1. **Speed**: Tests run 3-5x faster with Haiku
2. **Cost**: Haiku is significantly cheaper per API call
3. **Flexibility**: Easy to switch models without code changes
4. **Production Safety**: Production code always uses the specified model
5. **CI-Friendly**: Fast tests enable frequent CI runs

## Migration Guide

To update an existing test:

```python
# Before
model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514")

# After
from .test_helpers import get_test_model_name
model = ClaudeCodeChatModel(model=get_test_model_name())
```

That's it! The test will now respect the `CLAUDE_TEST_MODEL` environment variable.
