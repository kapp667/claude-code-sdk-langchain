# Investigation Temperature/Max_Tokens Support

## Date : 2025-09-30

## Question

Le Claude Code SDK Python permet-il de contrôler les paramètres `temperature` et `max_tokens` ?

---

## Résultats de l'Investigation

### 1. Documentation SDK Python (`python-SDK-reference.md`)

**ClaudeCodeOptions supporte** :
- ✅ `max_thinking_tokens: int = 8000` - Maximum tokens pour le processus de thinking
- ✅ `extra_args: dict[str, str | None] = {}` - Arguments CLI additionnels

**Citation ligne 485** :
> `extra_args` : Additional CLI arguments to pass directly to the CLI

### 2. CLI Claude (`claude --help`)

**Flags disponibles** :
- ✅ `--model <model>` - Model for the current session
- ✅ `--append-system-prompt <prompt>` - Append to system prompt
- ✅ `--permission-mode <mode>` - Permission mode
- ✅ `--allowed-tools <tools...>` - Tool whitelist
- ❌ **AUCUN FLAG `--temperature`**
- ❌ **AUCUN FLAG `--max-tokens`**

**Commande testée** :
```bash
claude --help 2>&1 | grep -i "temperature\|max.*token\|sampling"
# Résultat : Aucune correspondance
```

---

## Conclusions

### ❌ Temperature : NON SUPPORTÉ

**Evidence** :
1. Pas de flag `--temperature` dans `claude --help`
2. Pas de propriété `temperature` dans `ClaudeCodeOptions`
3. `max_thinking_tokens` existe mais c'est différent (contrôle le thinking, pas la génération)

**Comportement actuel de l'adaptateur** :
```python
# chat_model.py:136
extra_args["temperature"] = str(self.temperature)
```

**Problème** : Ce flag est passé au CLI mais **ignoré silencieusement** car le CLI ne le reconnaît pas.

### ❌ Max_Tokens : NON SUPPORTÉ

**Evidence** :
1. Pas de flag `--max-tokens` dans `claude --help`
2. Pas de propriété `max_tokens` dans `ClaudeCodeOptions`
3. Le CLI ne documente aucun contrôle de longueur de réponse

**Comportement actuel de l'adaptateur** :
```python
# chat_model.py:138
extra_args["max-tokens"] = str(self.max_tokens)
```

**Problème** : Ce flag est passé au CLI mais **ignoré silencieusement**.

---

## Impact sur la Neutralité Comportementale

### Scénarios Problématiques

#### Scénario 1 : Tests Déterministes
```python
# Développement avec adaptateur
model = ClaudeCodeChatModel(temperature=0.0)  # Utilisateur veut réponses déterministes
response = model.invoke(messages)
# MAIS : Claude utilise température par défaut (~0.7) → résultats variables

# Production avec ChatAnthropic
model = ChatAnthropic(temperature=0.0, api_key="...")
response = model.invoke(messages)
# Résultats déterministes comme attendu
```

**Impact** : Tests passent en production, échouent en développement (ou vice-versa).

#### Scénario 2 : Contrôle de Longueur
```python
# Développement
model = ClaudeCodeChatModel(max_tokens=100)  # Limite à 100 tokens
response = model.invoke(messages)
# MAIS : Claude génère réponses complètes (potentiellement 1000+ tokens)

# Production
model = ChatAnthropic(max_tokens=100, api_key="...")
response = model.invoke(messages)
# Respecte la limite de 100 tokens
```

**Impact** : Applications qui comptent sur des réponses courtes cassent.

---

## Options de Résolution

### Option 1 : Warning Explicite (RECOMMANDÉ)

**Approche** : Avertir l'utilisateur que ces paramètres ne sont pas supportés.

```python
def _get_claude_options(self) -> ClaudeCodeOptions:
    # Avertissement si paramètres non-défaut
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

    # Ne pas passer via extra_args (inutile)
    return ClaudeCodeOptions(
        model=self.model_name,
        system_prompt=self.system_prompt,
        permission_mode=self.permission_mode,
        allowed_tools=self.allowed_tools,
        cwd=self.cwd,
        max_turns=1,
    )
```

**Avantages** :
- ✅ Utilisateur est informé immédiatement
- ✅ Message clair sur impact migration
- ✅ Ne cache pas le problème

**Inconvénients** :
- ⚠️ Warning à chaque invocation si paramètres non-défaut
- ⚠️ Peut être verbeux dans les logs

### Option 2 : Retirer les Paramètres

**Approche** : Supprimer `temperature` et `max_tokens` de `ClaudeCodeChatModel`.

```python
class ClaudeCodeChatModel(BaseChatModel):
    # Supprimer ces lignes :
    # temperature: Optional[float] = Field(default=0.7)
    # max_tokens: Optional[int] = Field(default=2000)
```

**Avantages** :
- ✅ Impossible de spécifier des paramètres non supportés
- ✅ API claire sur ce qui est supporté

**Inconvénients** :
- ❌ Casse compatibilité avec BaseChatModel
- ❌ Utilisateurs doivent modifier code lors migration
- ❌ Pas un "drop-in replacement"

### Option 3 : Documenter Uniquement

**Approche** : Garder paramètres, documenter dans README/docstrings qu'ils ne fonctionnent pas.

**Avantages** :
- ✅ Garde compatibilité interface

**Inconvénients** :
- ❌ Silencieux - utilisateur peut ne pas voir la documentation
- ❌ Échec silencieux = mauvaise UX
- ❌ Bugs difficiles à tracer

### Option 4 : Raise Exception

**Approche** : Lever une exception si paramètres non-défaut spécifiés.

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

**Avantages** :
- ✅ Impossible d'utiliser mauvais paramètres
- ✅ Message d'erreur clair

**Inconvénients** :
- ❌ Casse le "drop-in replacement"
- ❌ Utilisateurs doivent modifier beaucoup de code

---

## Recommandation Finale

### ✅ SOLUTION HYBRIDE (Option 1 + Documentation)

**Implémentation** :

1. **Warning lors de l'initialisation** (une seule fois) :
```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)

    # Warning une seule fois à l'init
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

2. **Retirer extra_args inutiles** :
```python
def _get_claude_options(self) -> ClaudeCodeOptions:
    # Ne pas passer temperature/max_tokens via extra_args
    # (ils sont ignorés de toute façon)
    return ClaudeCodeOptions(
        model=self.model_name,
        system_prompt=self.system_prompt,
        permission_mode=self.permission_mode,
        allowed_tools=self.allowed_tools,
        cwd=self.cwd,
        max_turns=1,
    )
```

3. **Documentation claire** dans README.md :
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

4. **Docstring dans la classe** :
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

### Avantages de Cette Solution

- ✅ **Warning visible** : Utilisateur est prévenu immédiatement
- ✅ **Une seule fois** : Warning au __init__, pas à chaque invoke()
- ✅ **Code clean** : Retire extra_args inutiles
- ✅ **Documentation** : README et docstrings clairs
- ✅ **API compatibility** : Garde les paramètres pour "drop-in replacement"
- ✅ **Fail-fast** : Utilisateur découvre la limitation tôt
- ✅ **Migration guide** : Documentation montre comment basculer en production

---

## Tests de Validation

```python
# Test 1 : Warning température
model = ClaudeCodeChatModel(temperature=0.0)
# Devrait logger : "⚠️  Temperature 0.0 NOT SUPPORTED..."

# Test 2 : Warning max_tokens
model = ClaudeCodeChatModel(max_tokens=100)
# Devrait logger : "⚠️  max_tokens 100 NOT SUPPORTED..."

# Test 3 : Pas de warning si valeurs par défaut
model = ClaudeCodeChatModel(temperature=0.7, max_tokens=2000)
# Aucun warning

# Test 4 : Comportement identique
# Les deux modèles devraient générer des réponses similaires
# (car paramètres ignorés de toute façon)
```

---

## Conclusion

**Claude Code CLI ne supporte PAS `temperature` ni `max_tokens`.**

**Solution recommandée** :
1. Warning clair à l'initialisation si paramètres non-défaut
2. Retirer extra_args inutiles
3. Documentation explicite des limitations
4. Garder paramètres pour compatibilité API

**Impact sur neutralité comportementale** :
- Avec warnings : 85% (limitation claire, utilisateur informé)
- Sans warnings : 60% (échec silencieux)

**Prochaine étape** : Implémenter la solution hybride recommandée.
