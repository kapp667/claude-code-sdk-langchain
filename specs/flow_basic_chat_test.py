"""
Test de flux : Chat basique avec ClaudeCodeChatModel
"""

import asyncio
import pytest
from langchain_core.messages import HumanMessage, AIMessage


def test_basic_chat_invocation():
    """Test d'invocation basique du modèle"""
    from src.claude_code_langchain import ClaudeCodeChatModel

    # Créer le modèle
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.7,
        max_tokens=500
    )

    # Tester l'invocation synchrone
    messages = [HumanMessage(content="Bonjour, qui es-tu?")]

    try:
        response = model.invoke(messages)

        # Valider la réponse avec assertions plus strictes
        assert response is not None, "La réponse ne devrait pas être None"
        assert isinstance(response, AIMessage), f"Type attendu: AIMessage, reçu: {type(response)}"
        assert len(response.content) > 0, "Le contenu de la réponse est vide"
        assert response.content != "", "Le contenu est une chaîne vide"
        assert not response.content.isspace(), "Le contenu ne contient que des espaces"

        # Vérifier que la réponse a du sens (contient au moins quelques mots)
        words = response.content.split()
        assert len(words) >= 3, f"Réponse trop courte: seulement {len(words)} mots"

        print(f"✅ Test basique réussi")
        print(f"   Réponse: {response.content[:100]}...")

    except Exception as e:
        pytest.fail(f"Échec du test basique: {e}")


@pytest.mark.asyncio
async def test_async_chat_invocation():
    """Test d'invocation asynchrone du modèle"""
    from src.claude_code_langchain import ClaudeCodeChatModel

    # Créer le modèle
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.5,
        max_tokens=300
    )

    # Tester l'invocation asynchrone
    messages = [HumanMessage(content="Explique LangChain en une phrase")]

    try:
        response = await model.ainvoke(messages)

        # Valider la réponse
        assert response is not None
        assert isinstance(response, AIMessage)
        assert len(response.content) > 0

        # Vérifier les métadonnées si disponibles
        if response.response_metadata:
            assert "model" in response.additional_kwargs or "session_id" in response.response_metadata

        print(f"✅ Test async réussi")
        print(f"   Réponse: {response.content}")

    except Exception as e:
        pytest.fail(f"Échec du test async: {e}")


def test_streaming_chat():
    """Test du streaming de réponses"""
    from src.claude_code_langchain import ClaudeCodeChatModel

    # Créer le modèle
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.7
    )

    # Tester le streaming
    messages = [HumanMessage(content="Compte de 1 à 5")]

    try:
        chunks_received = 0
        full_response = ""

        for chunk in model.stream(messages):
            chunks_received += 1
            full_response += chunk.content
            print(f"   Chunk {chunks_received}: {chunk.content}", end="")

        # Valider le streaming
        assert chunks_received > 0, "Aucun chunk reçu"
        assert len(full_response) > 0, "Réponse vide"

        print(f"\n✅ Test streaming réussi")
        print(f"   {chunks_received} chunks reçus")

    except Exception as e:
        pytest.fail(f"Échec du test streaming: {e}")


def test_with_system_prompt():
    """Test avec prompt système"""
    from src.claude_code_langchain import ClaudeCodeChatModel
    from langchain_core.messages import SystemMessage

    # Créer le modèle avec prompt système
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        system_prompt="Tu es un expert Python qui répond de manière concise.",
        temperature=0.3,
        max_tokens=200
    )

    # Tester avec message système
    messages = [
        SystemMessage(content="Réponds toujours en commençant par 'Python:'"),
        HumanMessage(content="Qu'est-ce qu'une liste?")
    ]

    try:
        response = model.invoke(messages)

        # Valider la réponse
        assert response is not None
        assert isinstance(response, AIMessage)
        assert len(response.content) > 0

        print(f"✅ Test avec système réussi")
        print(f"   Réponse: {response.content[:150]}...")

    except Exception as e:
        pytest.fail(f"Échec du test avec système: {e}")


if __name__ == "__main__":
    # Exécuter les tests manuellement
    print("🧪 Tests de flux ClaudeCodeChatModel\n")

    print("1. Test basique...")
    test_basic_chat_invocation()

    print("\n2. Test async...")
    asyncio.run(test_async_chat_invocation())

    print("\n3. Test streaming...")
    test_streaming_chat()

    print("\n4. Test avec système...")
    test_with_system_prompt()

    print("\n✅ Tous les tests sont passés!")