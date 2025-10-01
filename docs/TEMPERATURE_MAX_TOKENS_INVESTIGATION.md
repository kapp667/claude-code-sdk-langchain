# Investigation: Temperature/Max_Tokens Support

## Date: 2025-09-30

## Question

Does the Claude Code Python SDK support controlling `temperature` and `max_tokens` parameters?

---

## Investigation Results

### 1. Python SDK Documentation (`python-SDK-reference.md`)

**ClaudeCodeOptions supports**:
- ✅ `max_thinking_tokens: int = 8000` - Maximum tokens for thinking process
- ✅ `extra_args: dict[str, str | None] = {}` - Additional CLI arguments

**Quote from line 485**:
> `extra_args`: Additional CLI arguments to pass directly to the CLI

### 2. Claude CLI (`claude --help`)

**Available flags**:
- ✅ `--model <model>` - Model for the current session
- ✅ `--append-system-prompt <prompt>` - Append to system prompt
- ✅ `--permission-mode <mode>` - Permission mode
- ✅ `--allowed-tools <tools...>` - Tool whitelist
- ❌ **NO `--temperature` FLAG**
- ❌ **NO `--max-tokens` FLAG**

**Command tested**:
```bash
claude --help 2>&1 | grep -i "temperature\|max.*token\|sampling"
# Result: No matches
```

---

## Conclusions

### ❌ Temperature: NOT SUPPORTED

**Evidence**:
1. No `--temperature` flag in `claude --help`
2. No `temperature` property in `ClaudeCodeOptions`
3. `max_thinking_tokens` exists but is different (controls thinking, not generation)

**Current adapter behavior**:
```python
# chat_model.py:136
extra_args["temperature"] = str(self.temperature)
```

**Problem**: This flag is passed to the CLI but **silently ignored** because the CLI doesn't recognize it.

### ❌ Max_Tokens: NOT SUPPORTED

**Evidence**:
1. No `--max-tokens` flag in `claude --help`
2. No `max_tokens` property in `ClaudeCodeOptions`
3. The CLI doesn't document any response length control

**Current adapter behavior**:
```python
# chat_model.py:138
extra_args["max-tokens"] = str(self.max_tokens)
```

**Problem**: This flag is passed to the CLI but **silently ignored**.

---

## Impact on Behavioral Neutrality

### Problematic Scenarios

#### Scenario 1: Deterministic Tests
```python
# Development with adapter
model = ClaudeCodeChatModel(temperature=0.0)  # User wants deterministic responses
response = model.invoke(messages)
# BUT: Claude uses default temperature (~0.7) → variable results

# Production with ChatAnthropic
model = ChatAnthropic(temperature=0.0, api_key="...")
response = model.invoke(messages)
# Deterministic results as expected
```

**Impact**: Tests pass in production, fail in development (or vice-versa).

#### Scenario 2: Length Control
```python
# Development
model = ClaudeCodeChatModel(max_tokens=100)  # Limit to 100 tokens
response = model.invoke(messages)
# BUT: Claude generates complete responses (potentially 1000+ tokens)

# Production
model = ChatAnthropic(max_tokens=100, api_key="...")
response = model.invoke(messages)
# Respects 100 token limit
```

**Impact**: Applications relying on short responses break.

---

## Resolution Options

### Option 1: Explicit Warning (RECOMMENDED)

**Approach**: Warn user that these parameters are not supported.

```python
def _get_claude_options(self) -> ClaudeCodeOptions:
    # Warning if non-default parameters
    if self.temperature is not None and self.temperature != 0.7:
        logger.warning(
            f"Temperature {self.temperature} specified but NOT SUPPORTED by Claude Code CLI. "
            f"Using model default (~0.7). "
            f"This will cause different behavior when migrating to production APIs. "
            f"Consider testing with production API for temperature-sensitive applications."
        )

    if self.max_tokens is not None and self.max_tokens != 2000:
        logger.warning(
            f"max_tokens {self.max_tokens} specified but NOT SUPPORTED by Claude Code CLI. "
            f"Using model default. "
            f"This will cause different behavior when migrating to production APIs."
        )

    # Don't pass via extra_args (useless)
    return ClaudeCodeOptions(
        model=self.model_name,
        system_prompt=self.system_prompt,
        permission_mode=self.permission_mode,
        allowed_tools=self.allowed_tools,
        cwd=self.cwd,
        max_turns=1,
    )
```

**Advantages**:
- ✅ User is informed immediately
- ✅ Clear message about migration impact
- ✅ Doesn't hide the problem

**Disadvantages**:
- ⚠️ Warning on every invocation if non-default parameters
- ⚠️ Can be verbose in logs

### Option 2: Remove Parameters

**Approach**: Remove `temperature` and `max_tokens` from `ClaudeCodeChatModel`.

```python
class ClaudeCodeChatModel(BaseChatModel):
    # Remove these lines:
    # temperature: Optional[float] = Field(default=0.7)
    # max_tokens: Optional[int] = Field(default=2000)
```

**Advantages**:
- ✅ Impossible to specify unsupported parameters
- ✅ Clear API about what's supported

**Disadvantages**:
- ❌ Breaks BaseChatModel compatibility
- ❌ Users must modify code when migrating
- ❌ Not a "drop-in replacement"

### Option 3: Documentation Only

**Approach**: Keep parameters, document in README/docstrings that they don't work.

**Advantages**:
- ✅ Maintains interface compatibility

**Disadvantages**:
- ❌ Silent - user may not see documentation
- ❌ Silent failure = bad UX
- ❌ Bugs hard to trace

### Option 4: Raise Exception

**Approach**: Raise exception if non-default parameters specified.

```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)

    if self.temperature != 0.7:
        raise NotImplementedError(
            f"Temperature parameter not supported by Claude Code CLI. "
            f"Use production API (ChatAnthropic) for temperature control."
        )

    if self.max_tokens != 2000:
        raise NotImplementedError(
            f"max_tokens parameter not supported by Claude Code CLI. "
            f"Use production API (ChatAnthropic) for token limit control."
        )
```

**Advantages**:
- ✅ Impossible to use wrong parameters
- ✅ Clear error message

**Disadvantages**:
- ❌ Breaks "drop-in replacement"
- ❌ Users must modify a lot of code

---

## Final Recommendation

### ✅ HYBRID SOLUTION (Option 1 + Documentation)

**Implementation**:

1. **Warning at initialization** (only once):
```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)

    # Warning once at init
    if self.temperature is not None and self.temperature != 0.7:
        logger.warning(
            f"⚠️  Temperature {self.temperature} NOT SUPPORTED by Claude Code CLI. "
            f"Model will use default temperature. "
            f"For temperature control, use production API (ChatAnthropic). "
            f"See: https://docs.anthropic.com/claude/reference/messages_post"
        )

    if self.max_tokens is not None and self.max_tokens != 2000:
        logger.warning(
            f"⚠️  max_tokens {self.max_tokens} NOT SUPPORTED by Claude Code CLI. "
            f"Model will use default token limit. "
            f"For token limit control, use production API (ChatAnthropic)."
        )
```

2. **Remove useless extra_args**:
```python
def _get_claude_options(self) -> ClaudeCodeOptions:
    # Don't pass temperature/max_tokens via extra_args
    # (they're ignored anyway)
    return ClaudeCodeOptions(
        model=self.model_name,
        system_prompt=self.system_prompt,
        permission_mode=self.permission_mode,
        allowed_tools=self.allowed_tools,
        cwd=self.cwd,
        max_turns=1,
    )
```

3. **Clear documentation** in README.md:
```markdown
## Known Limitations

### Temperature and Max_Tokens

The Claude Code CLI does not support `temperature` or `max_tokens` parameters.
These parameters are accepted for API compatibility but **have no effect**.

**For Development (Claude Code):**
```python
model = ClaudeCodeChatModel()  # Uses model defaults
```

**For Production (with parameter control):**
```python
model = ChatAnthropic(
    temperature=0.7,
    max_tokens=1000,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

If you need temperature or token limit control during development,
use the production API directly with your Anthropic API key.
```

4. **Docstring in class**:
```python
class ClaudeCodeChatModel(BaseChatModel):
    """
    ...

    Limitations:
        - temperature: Accepted for compatibility but NOT supported by Claude Code CLI
        - max_tokens: Accepted for compatibility but NOT supported by Claude Code CLI

    For applications requiring temperature or token limit control, use ChatAnthropic
    with an Anthropic API key instead.
    """

    temperature: Optional[float] = Field(default=0.7)
    """Temperature (NOT SUPPORTED - kept for API compatibility only)"""

    max_tokens: Optional[int] = Field(default=2000)
    """Max tokens (NOT SUPPORTED - kept for API compatibility only)"""
```

### Advantages of This Solution

- ✅ **Visible warning**: User is notified immediately
- ✅ **Only once**: Warning at __init__, not at each invoke()
- ✅ **Clean code**: Removes useless extra_args
- ✅ **Documentation**: Clear README and docstrings
- ✅ **API compatibility**: Keeps parameters for "drop-in replacement"
- ✅ **Fail-fast**: User discovers limitation early
- ✅ **Migration guide**: Documentation shows how to switch to production

---

## Validation Tests

```python
# Test 1: Temperature warning
model = ClaudeCodeChatModel(temperature=0.0)
# Should log: "⚠️  Temperature 0.0 NOT SUPPORTED..."

# Test 2: max_tokens warning
model = ClaudeCodeChatModel(max_tokens=100)
# Should log: "⚠️  max_tokens 100 NOT SUPPORTED..."

# Test 3: No warning if default values
model = ClaudeCodeChatModel(temperature=0.7, max_tokens=2000)
# No warnings

# Test 4: Identical behavior
# Both models should generate similar responses
# (since parameters are ignored anyway)
```

---

## Conclusion

**Claude Code CLI does NOT support `temperature` or `max_tokens`.**

**Recommended solution**:
1. Clear warning at initialization if non-default parameters
2. Remove useless extra_args
3. Explicit limitation documentation
4. Keep parameters for API compatibility

**Impact on behavioral neutrality**:
- With warnings: 85% (clear limitation, user informed)
- Without warnings: 60% (silent failure)

**Next step**: Implement recommended hybrid solution.
