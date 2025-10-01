# Contributing to Claude Code SDK - LangChain Adapter

Thank you for your interest in contributing! This document explains the project structure, testing philosophy, and development workflow.

## Project Structure

This project follows a specific organizational pattern to maintain clarity and ease of maintenance:

### Directory Organization

```
claude-code-sdk-langchain/
├── src/                    # Source code
│   ├── claude_code_langchain/  # Main package
│   └── __INDEX.md          # Directory index
├── specs/                  # Pragmatic flow tests
│   ├── flow_*.md           # Flow descriptions
│   ├── flow_*_test.py      # Flow test implementations
│   ├── README.md           # Testing philosophy
│   └── __INDEX.md          # Directory index
├── docs/                   # Technical documentation
│   └── __INDEX.md          # Directory index
├── examples/               # Usage examples
├── scripts/                # Automation scripts
│   └── __INDEX.md          # Directory index
├── data/                   # Production data
│   └── __INDEX.md          # Directory index
├── tmp/                    # Temporary files (not versioned)
└── dist/                   # Build artifacts (not versioned)
```

### __INDEX.md Files

Each significant directory contains an `__INDEX.md` file (double underscore) that serves as a navigation aid:

**Purpose:**
- Quick reference for directory contents
- Brief description of each file's role
- Creation and modification dates
- Maintained manually when files are added/modified

**Format:**
```markdown
# __INDEX - directory_name

## file_name.py
Description: Brief description of what this file does
Created: YYYY-MM-DD
Modified: YYYY-MM-DD
```

**When to Update:**
- Creating a new file → Add entry to __INDEX.md
- Significantly modifying a file → Update "Modified" date and description if needed
- Removing a file → Remove entry from __INDEX.md

## Testing Philosophy: Pragmatic Flow Testing

This project uses **Pragmatic Flow Testing** - a testing approach optimized for LLM-assisted development.

### Core Principles

1. **Test Through Public APIs Only**
   - Test what users actually use
   - No testing of private methods or implementation details
   - Treat components as black boxes

2. **Focus on User Journeys**
   - Each test represents a real user flow
   - End-to-end testing from user perspective
   - No mocking or artificial isolation

3. **LLM as Unit Test**
   - LLMs naturally validate logic during code generation
   - Explicit tests for flows, not unit-level details
   - Reduces test maintenance overhead by 80%

4. **Environmental Isolation via Pixi**
   - Reproducible environments without mocking
   - Deterministic test execution
   - Real dependencies, isolated context

### Test Structure

Each flow has two components:

1. **Flow Description** (`specs/flow_name.md`)
   - Markdown document describing the user journey
   - Step-by-step flow explanation
   - Expected outcomes

2. **Flow Test** (`specs/flow_name_test.py`)
   - Pytest implementation
   - Tests ONLY through public APIs
   - Can be run independently

**Example:**
```python
# specs/flow_basic_chat_test.py
"""Test basic chat flow (see flow_basic_chat.md)"""

def test_basic_invocation():
    from claude_code_langchain import ClaudeCodeChatModel  # Public API

    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514")
    response = model.invoke("What is LangChain?")  # Public method

    assert len(response.content) > 0  # Behavioral validation
```

### What to Test

✅ **DO Test:**
- Public API methods (invoke, stream, astream)
- User-visible behavior
- Integration with LangChain components
- Error messages users will see
- End-to-end flows

❌ **DON'T Test:**
- Private methods (_method_name)
- Internal state or attributes
- Implementation details
- Code the LLM validates during generation

### Running Tests

```bash
# All flow tests
pytest specs/

# Specific flow
python specs/flow_basic_chat_test.py

# With Pixi
pixi run pytest specs/
```

## Development Workflow

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/kapp667/claude-code-sdk-langchain.git
cd claude-code-sdk-langchain

# Enter Pixi environment (installs everything automatically)
pixi shell

# Verify installation
python -c "from claude_code_langchain import ClaudeCodeChatModel; print('✅ Setup complete')"
```

### 2. Making Changes

1. **Create a branch** (optional but recommended)
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style
   - Update __INDEX.md if adding/modifying files
   - Add/update flow tests if changing behavior

3. **Run tests**
   ```bash
   pixi run pytest specs/
   ```

4. **Update CHANGELOG.md**
   - Add entry describing your changes
   - Follow the existing format (see CHANGELOG.md)

### 3. Code Style

- **Python:** Follow PEP 8
  ```bash
  pixi run lint      # Check style
  pixi run format    # Auto-format
  ```

- **Comments:** English only
- **Docstrings:** Use for public APIs
- **Type hints:** Encouraged but not required

### 4. Documentation

- **README.md:** User-facing documentation
- **CLAUDE.md:** Internal guidance for Claude Code instances (local only)
- **docs/:** Technical reports and investigations
- **Flow descriptions:** User journey documentation

### 5. Commit Guidelines

Follow conventional commits:

```
type(scope): description

- feat: New feature
- fix: Bug fix
- docs: Documentation only
- refactor: Code restructuring
- test: Test additions/changes
- chore: Maintenance tasks
```

**Example:**
```bash
git commit -m "feat(streaming): add support for async streaming with parsers"
```

### 6. Pull Requests

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create PR on GitHub**
   - Clear description of changes
   - Link to related issues
   - Include test results

## Project-Specific Notes

### Critical Model Name

Always use `claude-sonnet-4-20250514` as the default model. This has been explicitly confirmed and must not regress to 3.5 or Opus.

### Behavioral Neutrality

The adapter aims for ~95% behavioral neutrality with the production Anthropic API. When adding features:
- Document any deviations from ChatAnthropic behavior
- Emit warnings for unsupported features
- Maintain API compatibility even if features don't work

### Local-Only Files

These files are excluded from the public repository:
- `CLAUDE.md` - Internal guidance
- `IMPORTANT_MODEL_NOTE.md` - Critical model name documentation
- `tmp/` - Temporary files

## Getting Help

- **Issues:** https://github.com/kapp667/claude-code-sdk-langchain/issues
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** See README.md and docs/

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
