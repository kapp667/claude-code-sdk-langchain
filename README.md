# Claude Code SDK - LangChain Adapter

Utilisez Claude via votre abonnement Claude Code (20$/mois) comme modèle LLM dans LangChain pour prototyper des applications agentiques **SANS frais API supplémentaires** !

## 🎯 Objectif

Cet adaptateur permet d'utiliser votre abonnement Claude Code existant comme backend pour LangChain, vous permettant de :
- ✅ Prototyper des applications LangChain gratuitement (via votre abonnement)
- ✅ Tester des idées d'agents sans se soucier des coûts API
- ✅ Migrer facilement vers l'API officielle en production

## 📦 Installation

```bash
# 1. Installer les dépendances
pip install claude-code-sdk langchain langchain-core

# 2. S'assurer que Claude Code CLI est installé
npm install -g @anthropic-ai/claude-code
```

## 🚀 Utilisation Rapide

```python
from src.claude_code_langchain import ClaudeCodeChatModel
from langchain_core.prompts import ChatPromptTemplate

# Créer le modèle (utilise votre abonnement Claude Code)
model = ClaudeCodeChatModel(
    model="claude-sonnet-4-20250514",
    temperature=0.7
)

# Utilisation simple
response = model.invoke("Qu'est-ce que LangChain?")
print(response.content)

# Dans une chaîne LangChain
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant expert en {domain}"),
    ("human", "{question}")
])

chain = prompt | model
result = chain.invoke({
    "domain": "Python",
    "question": "Comment créer une API REST?"
})
```

## 🔄 Streaming

```python
# Streaming de réponses
for chunk in model.stream("Raconte une histoire"):
    print(chunk.content, end="")

# Streaming asynchrone
async for chunk in model.astream("Liste 5 idées"):
    print(chunk.content, end="")
```

## 🔗 Intégration LangChain Complète

L'adaptateur supporte toutes les fonctionnalités LangChain :
- ✅ Invocation synchrone/asynchrone
- ✅ Streaming
- ✅ Batch processing
- ✅ Intégration LCEL (LangChain Expression Language)
- ✅ Chaînes et agents

## 📝 Exemples

Voir le dossier `examples/` pour des exemples complets :
- `basic_usage.py` - Exemples d'utilisation variés
- Tests dans `specs/` - Tests de flux pragmatiques

## 🧪 Tests

```bash
# Exécuter les tests de flux
python specs/flow_basic_chat_test.py
python specs/flow_langchain_integration_test.py

# Ou avec pytest
pytest specs/
```

## 🔄 Migration vers Production

Quand vous êtes prêt pour la production, remplacez simplement :

```python
# Développement (votre abonnement)
from src.claude_code_langchain import ClaudeCodeChatModel
model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514")

# Production (API officielle)
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-opus-20240229", api_key="sk-...")
```

Le reste de votre code reste identique !

## ⚙️ Configuration

```python
model = ClaudeCodeChatModel(
    model="claude-sonnet-4-20250514",     # Modèle Claude Sonnet 4
    temperature=0.7,                      # ⚠️ NON SUPPORTÉ (valeur ignorée)
    max_tokens=2000,                      # ⚠️ NON SUPPORTÉ (valeur ignorée)
    system_prompt="Tu es un expert...",  # Prompt système
    permission_mode="default",            # Mode permissions Claude Code
)
```

## 🏗️ Architecture

```
LangChain App
     ↓
ClaudeCodeChatModel (cet adaptateur)
     ↓
claude-code-sdk (SDK Python)
     ↓
Claude Code CLI
     ↓
Claude (via votre abonnement)
```

## ⚠️ Limitations et Avertissements

Cette section documente les limitations connues de l'adaptateur. Ces limitations sont **intentionnelles** - elles représentent les trade-offs entre prototypage cost-free et API de production. L'adaptateur émet des **warnings runtime** pour vous prévenir quand vous utilisez des fonctionnalités non supportées.

### 🌡️ Temperature et Max_Tokens

**Limitation** : Le Claude Code CLI ne supporte pas les paramètres `temperature` et `max_tokens`.

**Comportement** :
- Ces paramètres sont **acceptés pour compatibilité API** (évite de casser votre code)
- Ils **n'ont aucun effet** sur la génération
- Un **warning est émis** au moment de l'initialisation si vous spécifiez des valeurs non-défaut

**Pour le Développement (Claude Code):**
```python
model = ClaudeCodeChatModel()  # Utilise les valeurs par défaut du modèle
# ⚠️ temperature=0.7 et max_tokens=2000 n'auront aucun effet
```

**Pour la Production (avec contrôle des paramètres):**
```python
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(
    temperature=0.7,      # ✅ Fonctionne en production
    max_tokens=1000,      # ✅ Fonctionne en production
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

**Pourquoi ?** Le CLI Claude Code ne expose pas de flags `--temperature` ou `--max-tokens`. Investigation complète : [`docs/TEMPERATURE_MAX_TOKENS_INVESTIGATION.md`](docs/TEMPERATURE_MAX_TOKENS_INVESTIGATION.md)

**Solution** : Si vous avez besoin du contrôle de température ou de limite de tokens pendant le développement, utilisez directement l'API de production avec votre clé API Anthropic.

---

### 🖼️ Vision et Contenu Multimodal

**Limitation** : Les images et autres contenus non-texte ne sont pas supportés.

**Comportement** :
- Le texte est extrait et traité
- Les images sont **silencieusement ignorées**
- Un **warning est émis** quand une image est détectée dans les messages

**Exemple** :
```python
messages = [
    HumanMessage(content=[
        {"type": "text", "text": "Décris cette image"},
        {"type": "image_url", "image_url": {"url": "https://..."}}  # ⚠️ Ignoré
    ])
]
# Warning: Image content detected but NOT SUPPORTED by Claude Code SDK
```

**Pourquoi ?** Le SDK Claude Code ne gère pas les messages multimodaux via le CLI.

**Solution** : Pour les tâches vision, utilisez `ChatAnthropic` avec l'API de production qui supporte vision nativement.

---

### 🔄 Support Async

**Support Complet** ✅ : L'adaptateur supporte maintenant complètement les opérations asynchrones grâce à un fix d'isolation anyio.

**✅ Opérations Sync (100%)**
- `model.invoke()` - Support complet
- `model.stream()` - Support complet
- `model.batch()` - Support complet
- Chaînes avec exécution sync - Support complet

**✅ Opérations Async (100%)**
- `model.ainvoke()` - Support complet
- `model.astream()` - Streaming complet avec isolation anyio
- `chain.astream()` avec parsers - **Support complet** (fix anyio/asyncio via queue)
- Cancellation de stream - Supporté via break ou cancel()

**Tests** : 16/16 tests fonctionnels passent (100%) ✅

**Note technique** : Un problème `RuntimeError: cancel scope in different task` avec LangChain parsers a été résolu via un pattern de queue isolation. Détails : [`CLAUDE.md`](CLAUDE.md#critical-implementation-details)

---

### 🔧 System Prompt - Conflit de Sources

**Limitation** : Si vous spécifiez un `system_prompt` dans le constructor ET un `SystemMessage` dans les messages, il y a précédence.

**Comportement** :
- `SystemMessage` dans les messages **prend précédence**
- Constructor `system_prompt` est **ignoré**
- Un **warning est émis** si les deux sont présents

**Pourquoi ?** Pour éviter d'avoir deux system prompts contradictoires et assurer un comportement prévisible.

---

### ⚡ Autres Limitations

| Limitation | Impact | Solution |
|------------|--------|----------|
| **Tool calls** | Pas de support natif | Peut être simulé via prompting explicite |
| **Latence** | +10-30% vs API directe | Trade-off acceptable pour prototypage |
| **CLI Required** | Nécessite `npm install -g @anthropic-ai/claude-code` | Installation une fois |
| **Quotas** | Limités par votre abonnement Claude Code | Passer à API production si dépassé |

---

### 📊 Neutralité Comportementale

**Score global** : ~95%

L'adaptateur maintient une **haute neutralité comportementale** avec l'API de production :
- ✅ Messages et formats : 100% compatible
- ✅ Streaming et async : 100% compatible
- ⚠️ Paramètres sampling : Non supporté (temperature, max_tokens)
- ⚠️ Vision : Non supporté
- ✅ Comportement core : Identique à ChatAnthropic

**Validation** : 3 agents spécialisés ont analysé l'implémentation. Rapport complet : [`docs/VALIDATION_REPORT_2025-09-30.md`](docs/VALIDATION_REPORT_2025-09-30.md)

---

### 💡 Recommandations

**Pour le Prototypage** (cet adaptateur) :
- ✅ Notebooks Jupyter
- ✅ Scripts CLI de test
- ✅ Chaînes LangChain basiques et complexes
- ✅ Agents simples
- ✅ Expérimentation rapide

**Pour la Production** (ChatAnthropic) :
- ✅ Applications nécessitant temperature control
- ✅ Tâches vision/multimodal
- ✅ Déploiements à grande échelle
- ✅ Contrôle précis de la génération
- ✅ Tool calls natifs

**Migration** : Changer une ligne de code suffit (voir section Migration Path ci-dessus).

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :
- Ajouter des fonctionnalités
- Améliorer la documentation
- Rapporter des bugs
- Proposer des optimisations

## 📄 Licence

MIT

## 🙏 Remerciements

- Anthropic pour Claude et Claude Code
- LangChain pour le framework
- Stéphane Wootha Richard pour l'orchestration

---

**Note** : Cet adaptateur est parfait pour le prototypage et le développement. Pour la production à grande échelle, considérez l'API officielle Anthropic.