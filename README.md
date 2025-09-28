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
    temperature=0.7,                      # Créativité (0-1)
    max_tokens=2000,                      # Tokens max
    system_prompt="Tu es un expert...",  # Prompt système
    permission_mode="default",            # Mode permissions Claude Code
    use_continuous_session=False         # Session avec mémoire
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

## ⚠️ Limitations

- Pas de support natif des tool calls (peut être ajouté via prompting)
- Latence potentiellement plus élevée que l'API directe
- Nécessite Claude Code CLI installé localement
- Limité par les quotas de votre abonnement Claude Code

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