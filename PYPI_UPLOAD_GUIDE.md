# PyPI Publication Guide

## Package Ready ✅

The `claude-code-langchain` v0.1.0 package is built and validated:
- ✅ `dist/claude_code_langchain-0.1.0-py3-none-any.whl` (wheel)
- ✅ `dist/claude_code_langchain-0.1.0.tar.gz` (source distribution)
- ✅ PyPI metadata validated (`twine check` passed)
- ✅ CLAUDE.md excluded from distribution

## Steps to Publish

### 1. Create a PyPI Account (if necessary)
- Go to https://pypi.org/account/register/
- Verify email

### 2. Create an API Token
- Go to https://pypi.org/manage/account/token/
- Click "Add API token"
- Name: "claude-code-langchain-upload"
- Scope: "Entire account" (or project-specific after first upload)
- Copy the token (starts with `pypi-...`)

### 3. Upload with Token

**Option A - Via command line**:
```bash
pixi run twine upload dist/* --username __token__ --password pypi-YOUR_TOKEN_HERE
```

**Option B - Via .pypirc file** (more secure):
```bash
# Create ~/.pypirc
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
EOF

# Protect the file
chmod 600 ~/.pypirc

# Upload
pixi run twine upload dist/*
```

### 4. Verify Publication
After successful upload:
- Package visible at: https://pypi.org/project/claude-code-langchain/
- Test installation: `pip install claude-code-langchain`

## User Installation

### Via pip
```bash
pip install claude-code-langchain
```

### Via Pixi
```bash
pixi add --pypi claude-code-langchain
```

### Via Poetry
```bash
poetry add claude-code-langchain
```

## Update README.md

After publication, the installation section in README.md already includes:

```markdown
## 📦 Installation

```bash
# Via pip
pip install claude-code-langchain

# Via pixi
pixi add --pypi claude-code-langchain

# Via poetry
poetry add claude-code-langchain

# For development
pip install claude-code-langchain[dev]
```
```

## Important Notes

- ⚠️ The package name on PyPI is **`claude-code-langchain`** (with hyphens)
- ⚠️ The Python import module is **`claude_code_langchain`** (with underscores)
- ⚠️ Current version: **0.1.0** (Beta)
- ⚠️ First publication = irreversible (cannot delete from PyPI)

## Publishing a New Version

To publish v0.1.1 or v0.2.0:

```bash
# 1. Update version in pyproject.toml
# 2. Clean old distributions
rm -rf dist/

# 3. Rebuild
pixi run python -m build

# 4. Upload
pixi run twine upload dist/*
```

## Test on TestPyPI (Optional)

Before final publication, test on TestPyPI:

```bash
# Upload to TestPyPI
pixi run twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ claude-code-langchain
```

## Troubleshooting

### Error "File already exists"
- Cannot re-upload the same version
- Increment version in `pyproject.toml`

### Error "Invalid credentials"
- Verify token starts with `pypi-`
- Username must be exactly `__token__` (with underscores)

### Error "Package name already taken"
- The name `claude-code-langchain` is unique
- If taken, choose another name in `pyproject.toml`
