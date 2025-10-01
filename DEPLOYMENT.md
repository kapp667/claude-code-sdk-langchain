# Deployment Guide

Simple deployment guide for `claude-code-langchain` focused on GitHub distribution.

## Quick Deploy with Pixi

```bash
# Build package and prepare for GitHub release
pixi run deploy

# Build with tests
pixi run deploy-with-tests

# Build and create git tag
pixi run deploy-tag
```

## GitHub Distribution (Recommended)

**Simple and effective** - No API tokens, no complexity

### Prerequisites

- Git repository access
- GitHub account with push permissions

### Deployment Steps

1. **Build the package**:
```bash
pixi run deploy
```

This will:
- Run quality checks (format, lint, typecheck)
- Build wheel and tarball
- Validate package
- Display instructions for GitHub release

2. **Create GitHub Release**:
- Go to: https://github.com/kapp667/claude-code-sdk-langchain/releases/new
- Tag version: `v0.1.0` (matches pyproject.toml)
- Release title: `Release v0.1.0`
- Attach files from `dist/` directory:
  - `claude_code_langchain-0.1.0-py3-none-any.whl`
  - `claude_code_langchain-0.1.0.tar.gz`

3. **Users can install via**:
```bash
# Latest from main branch
pip install git+https://github.com/kapp667/claude-code-sdk-langchain.git

# Specific version tag
pip install git+https://github.com/kapp667/claude-code-sdk-langchain.git@v0.1.0

# Or download wheel from release
pip install claude_code_langchain-0.1.0-py3-none-any.whl
```

### Update Package

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Build: `pixi run deploy-tag`
4. Create GitHub release with new tag
5. Attach new dist files

### Advantages

✅ No API tokens required
✅ No PyPI complexity
✅ Direct git install
✅ Version control via tags
✅ Release notes on GitHub
✅ Free for open source

---

## Alternative: PyPI Distribution

If you want to publish to PyPI later, you'll need:

1. PyPI account at https://pypi.org
2. API token from https://pypi.org/manage/account/token/
3. Configure `~/.pypirc` with token
4. Install twine: `pixi add twine`
5. Add publish tasks to `pixi.toml`

For now, GitHub distribution is simpler and sufficient for most use cases.

---

## Pixi Integration

Users with Pixi can add to their `pixi.toml`:

```toml
[pypi-dependencies]
# From GitHub
claude-code-langchain = { git = "https://github.com/kapp667/claude-code-sdk-langchain.git" }

# Or specific version
claude-code-langchain = { git = "https://github.com/kapp667/claude-code-sdk-langchain.git", tag = "v0.1.0" }
```

---

## Local Development Install

For contributors:

```bash
# Clone repository
git clone https://github.com/kapp667/claude-code-sdk-langchain.git
cd claude-code-sdk-langchain

# Enter Pixi environment
pixi shell

# Editable install
pip install -e .

# Run tests
pixi run test

# Make changes and test
pixi run check  # format, lint, typecheck
```

---

## Version Management

**Current version**: Check `pyproject.toml`

**Update version**:
1. Edit `pyproject.toml`: `version = "0.1.1"`
2. Update `CHANGELOG.md`
3. Commit: `git commit -am "chore: bump version to 0.1.1"`
4. Deploy: `pixi run deploy-tag`
5. Create GitHub release

**Semantic Versioning**:
- `0.1.0 → 0.1.1`: Bug fixes
- `0.1.0 → 0.2.0`: New features (backward compatible)
- `0.1.0 → 1.0.0`: Breaking changes

---

## Distribution Files

After `pixi run deploy`, you'll find in `dist/`:

- **Wheel** (`.whl`): Binary distribution, faster install
- **Tarball** (`.tar.gz`): Source distribution, more compatible

Both should be attached to GitHub releases.

---

## Troubleshooting

**Build fails**:
```bash
pixi run clean-build
pixi run deploy-with-tests  # Include tests
```

**Tests timeout**:
```bash
# Tests use Haiku by default (fast)
export CLAUDE_TEST_MODEL=haiku
pixi run test
```

**Quality checks fail**:
```bash
pixi run format  # Auto-fix formatting
pixi run lint    # Check linting
pixi run typecheck  # Type checking
```

---

## Questions?

- Issues: https://github.com/kapp667/claude-code-sdk-langchain/issues
- Discussions: https://github.com/kapp667/claude-code-sdk-langchain/discussions
