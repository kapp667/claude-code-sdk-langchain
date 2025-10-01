# Guide de Publication sur PyPI

## Package Prêt ✅

Le package `claude-code-langchain` v0.1.0 est construit et validé :
- ✅ `dist/claude_code_langchain-0.1.0-py3-none-any.whl` (wheel)
- ✅ `dist/claude_code_langchain-0.1.0.tar.gz` (source distribution)
- ✅ Metadata PyPI validée (`twine check` passed)
- ✅ CLAUDE.md exclu de la distribution

## Étapes pour Publier

### 1. Créer un Compte PyPI (si nécessaire)
- Aller sur https://pypi.org/account/register/
- Vérifier l'email

### 2. Créer un Token API
- Aller sur https://pypi.org/manage/account/token/
- Cliquer "Add API token"
- Nom : "claude-code-langchain-upload"
- Scope : "Entire account" (ou spécifique au projet après premier upload)
- Copier le token (commence par `pypi-...`)

### 3. Uploader avec le Token

**Option A - Via ligne de commande** :
```bash
pixi run twine upload dist/* --username __token__ --password pypi-YOUR_TOKEN_HERE
```

**Option B - Via fichier .pypirc** (plus sécurisé) :
```bash
# Créer ~/.pypirc
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
EOF

# Protéger le fichier
chmod 600 ~/.pypirc

# Upload
pixi run twine upload dist/*
```

### 4. Vérifier la Publication
Après upload réussi :
- Package visible sur : https://pypi.org/project/claude-code-langchain/
- Installation testable : `pip install claude-code-langchain`

## Installation par les Utilisateurs

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

## Mettre à jour le README.md

Après publication, mettre à jour la section installation dans README.md :

```markdown
## 📦 Installation

```bash
# Via pip
pip install claude-code-langchain

# Via pixi
pixi add --pypi claude-code-langchain

# Via poetry
poetry add claude-code-langchain

# Pour développement
pip install claude-code-langchain[dev]
```
```

## Notes Importantes

- ⚠️ Le nom du package sur PyPI est **`claude-code-langchain`** (avec tirets)
- ⚠️ Le module Python importé est **`claude_code_langchain`** (avec underscores)
- ⚠️ Version actuelle : **0.1.0** (Beta)
- ⚠️ Première publication = irréversible (impossible de supprimer de PyPI)

## Publier une Nouvelle Version

Pour publier v0.1.1 ou v0.2.0 :

```bash
# 1. Mettre à jour la version dans pyproject.toml
# 2. Nettoyer les anciennes distributions
rm -rf dist/

# 3. Rebuild
pixi run python -m build

# 4. Upload
pixi run twine upload dist/*
```

## Test sur TestPyPI (Optionnel)

Avant publication finale, tester sur TestPyPI :

```bash
# Upload sur TestPyPI
pixi run twine upload --repository testpypi dist/*

# Installer depuis TestPyPI
pip install --index-url https://test.pypi.org/simple/ claude-code-langchain
```

## Troubleshooting

### Erreur "File already exists"
- Impossible de re-uploader la même version
- Incrémenter la version dans `pyproject.toml`

### Erreur "Invalid credentials"
- Vérifier que le token commence par `pypi-`
- Username doit être exactement `__token__` (avec underscores)

### Erreur "Package name already taken"
- Le nom `claude-code-langchain` est unique
- Si pris, choisir un autre nom dans `pyproject.toml`
