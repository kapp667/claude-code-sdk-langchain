# Deployment Guide

Complete guide for deploying `claude-code-langchain` to various package managers and distribution platforms.

## Quick Deploy with Pixi

```bash
# Complete deployment pipeline (runs tests, checks, builds, and publishes to PyPI)
pixi run publish

# Or step-by-step:
pixi run check          # Run all quality checks (format, lint, typecheck)
pixi run test           # Run all tests
pixi run build-package  # Build distribution packages
pixi run validate-package  # Validate with twine
pixi run publish-pypi   # Upload to PyPI (requires API token)
```

## 1. PyPI (Python Package Index)

**Official Python package repository** - Primary distribution method

### Prerequisites

```bash
# Install build tools (already in pixi.toml)
pip install build twine

# Create PyPI account at https://pypi.org
# Generate API token: https://pypi.org/manage/account/token/
```

### Configuration

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
```

### Deployment Steps

```bash
# Using Pixi (recommended)
pixi run publish

# Or manually:
pixi run clean-build
python -m build
twine check dist/*
twine upload dist/*

# Test on TestPyPI first:
pixi run publish-test
```

### Installation by Users

```bash
# Standard installation
pip install claude-code-langchain

# With development dependencies
pip install claude-code-langchain[dev]

# Latest from PyPI
pip install --upgrade claude-code-langchain
```

### Update Package

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run deployment: `pixi run publish`
4. Tag release: `git tag v0.1.1 && git push --tags`

---

## 2. Conda / Conda-Forge

**Conda ecosystem** - Scientific Python community

### Prerequisites

- Package must be on PyPI first
- Create conda-forge feedstock

### Steps

1. **Fork conda-forge/staged-recipes**
   ```bash
   git clone https://github.com/YOUR-USERNAME/staged-recipes.git
   cd staged-recipes
   ```

2. **Create recipe**
   Create `recipes/claude-code-langchain/meta.yaml`:
   ```yaml
   {% set name = "claude-code-langchain" %}
   {% set version = "0.1.0" %}

   package:
     name: {{ name|lower }}
     version: {{ version }}

   source:
     url: https://pypi.io/packages/source/{{ name[0] }}/{{ name }}/{{ name }}-{{ version }}.tar.gz
     sha256: CHECKSUM_FROM_PYPI

   build:
     noarch: python
     script: {{ PYTHON }} -m pip install . -vv
     number: 0

   requirements:
     host:
       - python >=3.11
       - pip
     run:
       - python >=3.11
       - langchain >=0.3.0
       - langchain-core >=0.3.0
       - claude-code-sdk >=0.0.23,<0.0.24
       - pydantic >=2.0

   test:
     imports:
       - claude_code_langchain
     commands:
       - pip check
     requires:
       - pip

   about:
     home: https://github.com/kapp667/claude-code-sdk-langchain
     license: MIT
     license_file: LICENSE
     summary: Use Claude via Claude Code subscription as LangChain model
     description: |
       Claude Code SDK adapter for LangChain - prototype agentic
       applications without API costs using Claude Code subscription.
     doc_url: https://github.com/kapp667/claude-code-sdk-langchain
     dev_url: https://github.com/kapp667/claude-code-sdk-langchain

   extra:
     recipe-maintainers:
       - kapp667
   ```

3. **Submit PR to conda-forge**
   ```bash
   git checkout -b add-claude-code-langchain
   git add recipes/claude-code-langchain/meta.yaml
   git commit -m "Add claude-code-langchain recipe"
   git push origin add-claude-code-langchain
   ```

4. **Create Pull Request**
   - Open PR on conda-forge/staged-recipes
   - Wait for review and CI checks
   - Once merged, feedstock is auto-created

### Installation by Users

```bash
conda install -c conda-forge claude-code-langchain
```

---

## 3. Poetry

**Modern Python dependency management**

### For Development

```bash
# Convert from setup.py/pyproject.toml
poetry init

# Or use existing pyproject.toml (compatible)
poetry install

# Add to another project
poetry add claude-code-langchain
```

### Publishing (Alternative to Twine)

```bash
poetry build
poetry publish

# Or with API token
poetry config pypi-token.pypi YOUR-PYPI-TOKEN
poetry publish
```

---

## 4. Pipenv

**Python dependency manager with virtualenv**

### Installation by Users

```bash
# Add to Pipfile
pipenv install claude-code-langchain

# Or direct install
pipenv install claude-code-langchain
```

---

## 5. GitHub Releases

**Distribute via GitHub releases**

### Manual Release

1. **Tag version**
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0: Initial public release"
   git push origin v0.1.0
   ```

2. **Create GitHub Release**
   - Go to https://github.com/kapp667/claude-code-sdk-langchain/releases/new
   - Select tag `v0.1.0`
   - Title: `v0.1.0 - Initial Release`
   - Description: Copy from CHANGELOG.md
   - Attach artifacts: `dist/*.whl` and `dist/*.tar.gz`
   - Publish release

### Automated with GitHub Actions

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
```

---

## 6. Direct Git Installation

**Install directly from GitHub**

### Installation by Users

```bash
# Latest from main branch
pip install git+https://github.com/kapp667/claude-code-sdk-langchain.git

# Specific tag/version
pip install git+https://github.com/kapp667/claude-code-sdk-langchain.git@v0.1.0

# Specific branch
pip install git+https://github.com/kapp667/claude-code-sdk-langchain.git@develop

# Editable mode for development
git clone https://github.com/kapp667/claude-code-sdk-langchain.git
cd claude-code-sdk-langchain
pip install -e .
```

---

## 7. Docker Distribution

**Containerized distribution**

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Install Python package
COPY . /app
RUN pip install --no-cache-dir /app

# Set environment
ENV PYTHONPATH=/app/src:$PYTHONPATH

CMD ["python"]
```

### Build and Publish

```bash
# Build image
docker build -t claude-code-langchain:0.1.0 .

# Tag for Docker Hub
docker tag claude-code-langchain:0.1.0 YOUR-USERNAME/claude-code-langchain:0.1.0
docker tag claude-code-langchain:0.1.0 YOUR-USERNAME/claude-code-langchain:latest

# Push to Docker Hub
docker push YOUR-USERNAME/claude-code-langchain:0.1.0
docker push YOUR-USERNAME/claude-code-langchain:latest
```

### Installation by Users

```bash
docker pull YOUR-USERNAME/claude-code-langchain:latest
docker run -it YOUR-USERNAME/claude-code-langchain:latest python
```

---

## Deployment Checklist

Before any release:

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with changes
- [ ] Run `pixi run check` - all checks pass
- [ ] Run `pixi run test` - all tests pass
- [ ] Update `README.md` if needed
- [ ] Build package: `pixi run build-package`
- [ ] Validate package: `pixi run validate-package`
- [ ] Test on TestPyPI: `pixi run publish-test`
- [ ] Publish to PyPI: `pixi run publish-pypi`
- [ ] Create git tag: `git tag v0.1.X`
- [ ] Push tag: `git push --tags`
- [ ] Create GitHub Release with artifacts
- [ ] Update conda-forge feedstock (if applicable)

---

## Version Numbering

Follow **Semantic Versioning** (semver.org):

- **MAJOR** (1.0.0): Breaking API changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.1.1): Bug fixes, backward compatible

Examples:
- `0.1.0` - Initial release
- `0.1.1` - Bug fixes
- `0.2.0` - New features (streaming support)
- `1.0.0` - Stable API, production ready

---

## Rollback Procedure

If a release has critical issues:

```bash
# 1. Yank the bad version from PyPI (doesn't delete, marks as unsafe)
# Visit: https://pypi.org/manage/project/claude-code-langchain/releases/

# 2. Fix issues locally
# 3. Increment patch version
# 4. Redeploy
pixi run publish

# 5. Announce issue and fixed version
```

---

## Support Matrix

| Platform | Status | Installation Command |
|----------|--------|---------------------|
| PyPI | ✅ Published | `pip install claude-code-langchain` |
| TestPyPI | ✅ Available | `pip install -i https://test.pypi.org/simple/ claude-code-langchain` |
| Conda-Forge | 🚧 Pending | `conda install -c conda-forge claude-code-langchain` |
| GitHub | ✅ Available | `pip install git+https://github.com/kapp667/claude-code-sdk-langchain.git` |
| Docker Hub | 📋 Planned | `docker pull USERNAME/claude-code-langchain` |
| Poetry | ✅ Compatible | `poetry add claude-code-langchain` |
| Pipenv | ✅ Compatible | `pipenv install claude-code-langchain` |

---

## Monitoring

After deployment:

- **PyPI Stats**: https://pypistats.org/packages/claude-code-langchain
- **GitHub Insights**: Check stars, forks, downloads
- **Issues**: Monitor for bug reports
- **Dependencies**: Use Dependabot for security updates

---

## Resources

- **PyPI Project**: https://pypi.org/project/claude-code-langchain/
- **GitHub Repository**: https://github.com/kapp667/claude-code-sdk-langchain
- **Documentation**: README.md and CONTRIBUTING.md
- **Packaging Guide**: https://packaging.python.org/
- **Conda-Forge**: https://conda-forge.org/docs/maintainer/adding_pkgs.html
