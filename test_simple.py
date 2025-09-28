#!/usr/bin/env python3
"""
Test ultra simple pour vérifier que l'adaptateur fonctionne
"""

import sys
import os

# Ajouter src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🧪 Test Simple ClaudeCodeChatModel\n")
    print("=" * 50)

    # 1. Import
    print("1️⃣  Import du module...")
    from claude_code_langchain import ClaudeCodeChatModel
    from langchain_core.messages import HumanMessage
    print("   ✅ Import réussi")

    # 2. Création du modèle
    print("\n2️⃣  Création du modèle...")
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.5,
        max_tokens=100
    )
    print("   ✅ Modèle créé")

    # 3. Test d'invocation simple
    print("\n3️⃣  Test d'invocation...")
    print("   Question: 'Qu'est-ce que 2+2?'")

    response = model.invoke([
        HumanMessage(content="Qu'est-ce que 2+2?")
    ])

    print(f"   ✅ Réponse reçue: {response.content}")

    # 4. Vérification du type
    print("\n4️⃣  Vérification du type de réponse...")
    from langchain_core.messages import AIMessage
    assert isinstance(response, AIMessage), "La réponse n'est pas un AIMessage"
    assert len(response.content) > 0, "La réponse est vide"
    print("   ✅ Type correct (AIMessage)")

    print("\n" + "=" * 50)
    print("🎉 TEST RÉUSSI ! L'adaptateur fonctionne !")
    print("=" * 50)

except ImportError as e:
    print(f"\n❌ Erreur d'import: {e}")
    print("\n💡 Assurez-vous que:")
    print("   1. claude-code-sdk est installé: pip install claude-code-sdk")
    print("   2. langchain est installé: pip install langchain langchain-core")
    print("   3. Claude Code CLI est installé: npm install -g @anthropic-ai/claude-code")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Erreur lors du test: {e}")
    print(f"   Type d'erreur: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)