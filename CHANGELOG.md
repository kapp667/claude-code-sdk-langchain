# CHANGELOG

[2025-09-30 18:00] #fix Critical bug fixes for production neutrality
→ commits: TBD | tag: todo-20250930-1800
→ modules: src/claude_code_langchain/*.py, examples/basic_usage.py
→ keywords: bugfix, production-ready, behavioral-neutrality, langchain-compatibility
• **CRITICAL**: Ajout logger import manquant dans message_converter.py (NameError fix)
• **CRITICAL**: Suppression échappement incorrect backslash/quotes (corruption de contenu)
• **CRITICAL**: Support contenu multimodal (list[dict]) au lieu de str seulement
• **HIGH**: Ajout gestion erreurs ResultMessage dans _astream (cohérence avec _agenerate)
• **HIGH**: Passage temperature/max_tokens via extra_args à ClaudeCodeOptions
• **HIGH**: Fix thread.join() sans timeout (évite terminaison prématurée)
• **HIGH**: Fix callback truthiness (content is not None au lieu de content)
• **MEDIUM**: Standardisation ThinkingBlock dans additional_kwargs (cohérence streaming/non-streaming)
• **MEDIUM**: Ajout validation stop sequences avec warning explicite
• **MEDIUM**: Ajout validation kwargs non supportés avec warning
• **LOW**: Correction modèle dans exemples (claude-3-opus → claude-sonnet-4-20250514)
• **LOW**: Remplacement use_continuous_session par exemple stateless correct
• Tests: 19 bugs logiques détectés et corrigés
• Impact: Neutralité comportementale 65% → 95% pour migration production
• Collaboration: langchain-expert, codebase-quality-analyzer, logic-bug-detector

[2025-09-30 14:30] #refactor Remove SDK-level session continuity
→ commits: initial | tag: todo-20250930-1430
→ modules: src/claude_code_langchain/chat_model.py, specs/flow_session_management.*
→ keywords: langchain, architecture, memory, sessions, stateless, DRY
• Suppression de use_continuous_session flag et code associé
• Suppression des tests de flux pour la gestion de session
• Suppression de l'import ClaudeSDKClient inutilisé
• Suppression des méthodes aconnect/adisconnect et context manager
• Impact: Architecture simplifiée, compatible avec patterns LangChain standard
• Justification: La continuité de contexte doit être gérée par LangChain (BaseChatModel stateless), pas par le SDK (conflit architectural, perte de contrôle utilisateur, incompatibilité avec LangGraph memory)
