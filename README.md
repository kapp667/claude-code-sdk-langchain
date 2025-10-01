# Claude Code SDK - LangChain Adapter

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangChain](https://img.shields.io/badge/LangChain-compatible-green.svg)](https://github.com/langchain-ai/langchain)
[![Status](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/kapp667/claude-code-sdk-langchain)

Use Claude via your Claude Code subscription ($20/month) as an LLM model in LangChain to prototype agentic applications **WITHOUT additional API fees**!

## 🎯 Purpose

This adapter allows you to use your existing Claude Code subscription as a backend for LangChain, enabling you to:
- ✅ Prototype LangChain applications for free (via your subscription)
- ✅ Test agent ideas without worrying about API costs
- ✅ Easily migrate to the official API in production

## 📦 Installation

### Via PyPI (Recommended)

```bash
# Full installation
pip install claude-code-langchain

# Or with development dependencies
pip install claude-code-langchain[dev]
```

### Via Pixi

```bash
pixi add --pypi claude-code-langchain
```

### Via Poetry

```bash
poetry add claude-code-langchain
```

### Via GitHub (Development Version)

```bash
pip install git+https://github.com/kapp667/claude-code-sdk-langchain.git
```

### Prerequisites

The **Claude Code CLI** must be installed and configured:

```bash
npm install -g @anthropic-ai/claude-code
```

## 🚀 Quick Start

```python
from claude_code_langchain import ClaudeCodeChatModel
from langchain_core.prompts import ChatPromptTemplate

# Create the model (uses your Claude Code subscription)
model = ClaudeCodeChatModel(
    model="claude-sonnet-4-20250514",
    temperature=0.7
)

# Simple usage
response = model.invoke("What is LangChain?")
print(response.content)

# In a LangChain chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}"),
    ("human", "{question}")
])

chain = prompt | model
result = chain.invoke({
    "domain": "Python",
    "question": "How to create a REST API?"
})
```

## 🔄 Streaming

```python
# Response streaming
for chunk in model.stream("Tell me a story"):
    print(chunk.content, end="")

# Async streaming
async for chunk in model.astream("List 5 ideas"):
    print(chunk.content, end="")
```

## 🔗 Full LangChain Integration

The adapter supports all LangChain features:
- ✅ Synchronous/asynchronous invocation
- ✅ Streaming
- ✅ Batch processing
- ✅ LCEL (LangChain Expression Language) integration
- ✅ Chains and agents

## 📝 Examples

See the `examples/` folder for complete examples:
- `basic_usage.py` - Various usage examples
- Tests in `specs/` - Pragmatic flow tests

## 🧪 Tests

```bash
# Run flow tests
python specs/flow_basic_chat_test.py
python specs/flow_langchain_integration_test.py

# Or with pytest
pytest specs/
```

## 🔄 Migration to Production

When you're ready for production, simply replace:

```python
# Development (your subscription)
from claude_code_langchain import ClaudeCodeChatModel
model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514")

# Production (official API)
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-opus-20240229", api_key="sk-...")
```

The rest of your code remains identical!

## ⚙️ Configuration

```python
model = ClaudeCodeChatModel(
    model="claude-sonnet-4-20250514",     # Claude Sonnet 4 model
    temperature=0.7,                      # ⚠️ NOT SUPPORTED (value ignored)
    max_tokens=2000,                      # ⚠️ NOT SUPPORTED (value ignored)
    system_prompt="You are an expert...", # System prompt
    permission_mode="default",            # Claude Code permission mode
)
```

## 🏗️ Architecture

```
LangChain App
     ↓
ClaudeCodeChatModel (this adapter)
     ↓
claude-code-sdk (Python SDK)
     ↓
Claude Code CLI
     ↓
Claude (via your subscription)
```

## ⚠️ Limitations and Warnings

This section documents the adapter's known limitations. These limitations are **intentional** - they represent the trade-offs between cost-free prototyping and production API. The adapter emits **runtime warnings** to alert you when using unsupported features.

### 🌡️ Temperature and Max_Tokens

**Limitation**: The Claude Code CLI does not support `temperature` and `max_tokens` parameters.

**Behavior**:
- These parameters are **accepted for API compatibility** (prevents breaking your code)
- They **have no effect** on generation
- A **warning is emitted** during initialization if you specify non-default values

**For Development (Claude Code):**
```python
model = ClaudeCodeChatModel()  # Uses model's default values
# ⚠️ temperature=0.7 and max_tokens=2000 will have no effect
```

**For Production (with parameter control):**
```python
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(
    temperature=0.7,      # ✅ Works in production
    max_tokens=1000,      # ✅ Works in production
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

**Why?** The Claude Code CLI does not expose `--temperature` or `--max-tokens` flags. Full investigation: [`docs/TEMPERATURE_MAX_TOKENS_INVESTIGATION.md`](docs/TEMPERATURE_MAX_TOKENS_INVESTIGATION.md)

**Solution**: If you need temperature control or token limits during development, use the production API directly with your Anthropic API key.

---

### 🖼️ Vision and Multimodal Content

**Limitation**: Images and other non-text content are not supported.

**Behavior**:
- Text is extracted and processed
- Images are **silently ignored**
- A **warning is emitted** when an image is detected in messages

**Example**:
```python
messages = [
    HumanMessage(content=[
        {"type": "text", "text": "Describe this image"},
        {"type": "image_url", "image_url": {"url": "https://..."}}  # ⚠️ Ignored
    ])
]
# Warning: Image content detected but NOT SUPPORTED by Claude Code SDK
```

**Why?** The Claude Code SDK does not handle multimodal messages via the CLI.

**Solution**: For vision tasks, use `ChatAnthropic` with the production API which natively supports vision.

---

### 🔄 Async Support

**Full Support** ✅: The adapter now fully supports asynchronous operations thanks to an anyio isolation fix.

**✅ Sync Operations (100%)**
- `model.invoke()` - Full support
- `model.stream()` - Full support
- `model.batch()` - Full support
- Chains with sync execution - Full support

**✅ Async Operations (100%)**
- `model.ainvoke()` - Full support
- `model.astream()` - Full streaming with anyio isolation
- `chain.astream()` with parsers - **Full support** (anyio/asyncio fix via queue)
- Stream cancellation - Supported via break or cancel()

**Tests**: 16/16 functional tests passing (100%) ✅

**Technical note**: A `RuntimeError: cancel scope in different task` issue with LangChain parsers was resolved via a queue isolation pattern. Details: [`CLAUDE.md`](CLAUDE.md#critical-implementation-details)

---

### 🔧 System Prompt - Source Conflict

**Limitation**: If you specify a `system_prompt` in the constructor AND a `SystemMessage` in the messages, there is precedence.

**Behavior**:
- `SystemMessage` in messages **takes precedence**
- Constructor `system_prompt` is **ignored**
- A **warning is emitted** if both are present

**Why?** To avoid having two contradictory system prompts and ensure predictable behavior.

---

### ⚡ Other Limitations

| Limitation | Impact | Solution |
|------------|--------|----------|
| **Tool calls** | No native support | Can be simulated via explicit prompting |
| **Latency** | +10-30% vs direct API | Acceptable trade-off for prototyping |
| **CLI Required** | Requires `npm install -g @anthropic-ai/claude-code` | One-time installation |
| **Quotas** | Limited by your Claude Code subscription | Switch to production API if exceeded |

---

### 📊 Behavioral Neutrality

**Overall Score**: ~95%

The adapter maintains **high behavioral neutrality** with the production API:
- ✅ Messages and formats: 100% compatible
- ✅ Streaming and async: 100% compatible
- ⚠️ Sampling parameters: Not supported (temperature, max_tokens)
- ⚠️ Vision: Not supported
- ✅ Core behavior: Identical to ChatAnthropic

**Validation**: 3 specialized agents analyzed the implementation. Full report: [`docs/VALIDATION_REPORT_2025-09-30.md`](docs/VALIDATION_REPORT_2025-09-30.md)

---

### 💡 Recommendations

**For Prototyping** (this adapter):
- ✅ Jupyter notebooks
- ✅ CLI test scripts
- ✅ Basic and complex LangChain chains
- ✅ Simple agents
- ✅ Rapid experimentation

**For Production** (ChatAnthropic):
- ✅ Applications requiring temperature control
- ✅ Vision/multimodal tasks
- ✅ Large-scale deployments
- ✅ Precise generation control
- ✅ Native tool calls

**Migration**: Changing one line of code is sufficient (see Migration Path section above).

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add features
- Improve documentation
- Report bugs
- Propose optimizations

## 📄 License

MIT

## 🙏 Acknowledgments

- Anthropic for Claude and Claude Code
- LangChain for the framework
- Stéphane Wootha Richard for orchestration

---

**Note**: This adapter is perfect for prototyping and development. For large-scale production, consider the official Anthropic API.
