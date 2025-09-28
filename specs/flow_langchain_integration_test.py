"""
Test de flux : Intégration avec chaînes LangChain
"""

import asyncio
import pytest
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage


def test_simple_chain():
    """Test d'une chaîne simple avec prompt et modèle"""
    from src.claude_code_langchain import ClaudeCodeChatModel

    # Créer les composants
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.5,
        max_tokens=200
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Tu es un assistant qui répond en {language}"),
        ("human", "{question}")
    ])

    # Créer la chaîne
    chain = prompt | model

    try:
        # Invoquer la chaîne
        response = chain.invoke({
            "language": "français",
            "question": "Qu'est-ce que Python?"
        })

        # Valider
        assert response is not None
        assert len(response.content) > 0

        print(f"✅ Test chaîne simple réussi")
        print(f"   Réponse: {response.content[:100]}...")

    except Exception as e:
        pytest.fail(f"Échec test chaîne simple: {e}")


def test_chain_with_parser():
    """Test d'une chaîne avec output parser"""
    from src.claude_code_langchain import ClaudeCodeChatModel

    # Créer les composants
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.3,
        max_tokens=150
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Réponds toujours de manière très concise"),
        ("human", "{input}")
    ])

    parser = StrOutputParser()

    # Créer la chaîne complète
    chain = prompt | model | parser

    try:
        # Invoquer la chaîne
        response = chain.invoke({
            "input": "Définis Python en 5 mots maximum"
        })

        # Valider que c'est bien une string parsée
        assert isinstance(response, str)
        assert len(response) > 0

        print(f"✅ Test chaîne avec parser réussi")
        print(f"   Réponse parsée: {response}")

    except Exception as e:
        pytest.fail(f"Échec test avec parser: {e}")


@pytest.mark.asyncio
async def test_async_chain():
    """Test d'une chaîne asynchrone"""
    from src.claude_code_langchain import ClaudeCodeChatModel

    # Créer les composants
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.7
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Tu es un expert en {domain}"),
        ("human", "Explique {concept}")
    ])

    chain = prompt | model | StrOutputParser()

    try:
        # Invoquer de manière asynchrone
        response = await chain.ainvoke({
            "domain": "informatique",
            "concept": "les algorithmes"
        })

        # Valider
        assert isinstance(response, str)
        assert len(response) > 0

        print(f"✅ Test chaîne async réussi")
        print(f"   Réponse: {response[:100]}...")

    except Exception as e:
        pytest.fail(f"Échec test async: {e}")


def test_batch_processing():
    """Test du traitement par batch"""
    from src.claude_code_langchain import ClaudeCodeChatModel

    # Créer le modèle
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.5,
        max_tokens=100
    )

    # Créer plusieurs messages
    batch_inputs = [
        [HumanMessage(content="Qu'est-ce que 2+2?")],
        [HumanMessage(content="Capitale de la France?")],
        [HumanMessage(content="Couleur du ciel?")]
    ]

    try:
        # Traiter en batch
        responses = model.batch(batch_inputs)

        # Valider
        assert len(responses) == 3
        for response in responses:
            assert response is not None
            assert len(response.content) > 0

        print(f"✅ Test batch réussi")
        print(f"   {len(responses)} réponses reçues")

    except Exception as e:
        pytest.fail(f"Échec test batch: {e}")


def test_streaming_chain():
    """Test du streaming dans une chaîne"""
    from src.claude_code_langchain import ClaudeCodeChatModel

    # Créer les composants
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.7
    )

    prompt = ChatPromptTemplate.from_messages([
        ("human", "Raconte une courte histoire sur {topic}")
    ])

    chain = prompt | model

    try:
        # Stream la réponse
        chunks_count = 0
        for chunk in chain.stream({"topic": "un robot"}):
            chunks_count += 1
            print(".", end="", flush=True)

        print()  # Nouvelle ligne
        assert chunks_count > 0

        print(f"✅ Test streaming chaîne réussi")
        print(f"   {chunks_count} chunks streamés")

    except Exception as e:
        pytest.fail(f"Échec test streaming: {e}")


def test_complex_chain_with_multiple_steps():
    """Test d'une chaîne complexe avec plusieurs étapes"""
    from src.claude_code_langchain import ClaudeCodeChatModel
    from langchain_core.runnables import RunnablePassthrough

    # Créer le modèle
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.5,
        max_tokens=150
    )

    # Première étape : classifier
    classify_prompt = ChatPromptTemplate.from_messages([
        ("system", "Classifie le texte suivant en 'positif', 'négatif' ou 'neutre'"),
        ("human", "{text}")
    ])

    # Deuxième étape : répondre selon la classification
    response_prompt = ChatPromptTemplate.from_messages([
        ("system", "Le sentiment est {sentiment}. Réponds de manière appropriée."),
        ("human", "Comment réagir à: {text}")
    ])

    # Chaîne complexe
    classify_chain = classify_prompt | model | StrOutputParser()

    def create_response_input(inputs):
        sentiment = classify_chain.invoke({"text": inputs["text"]})
        return {
            "sentiment": sentiment,
            "text": inputs["text"]
        }

    complex_chain = RunnablePassthrough.assign(
        sentiment=lambda x: classify_chain.invoke({"text": x["text"]})
    ) | response_prompt | model | StrOutputParser()

    try:
        # Test avec un texte
        response = complex_chain.invoke({
            "text": "Ce produit est absolument fantastique!"
        })

        # Valider
        assert isinstance(response, str)
        assert len(response) > 0

        print(f"✅ Test chaîne complexe réussi")
        print(f"   Réponse: {response[:150]}...")

    except Exception as e:
        pytest.fail(f"Échec test chaîne complexe: {e}")


if __name__ == "__main__":
    # Exécuter les tests
    print("🧪 Tests d'intégration LangChain\n")

    print("1. Test chaîne simple...")
    test_simple_chain()

    print("\n2. Test avec parser...")
    test_chain_with_parser()

    print("\n3. Test async...")
    asyncio.run(test_async_chain())

    print("\n4. Test batch...")
    test_batch_processing()

    print("\n5. Test streaming chaîne...")
    test_streaming_chain()

    print("\n6. Test chaîne complexe...")
    test_complex_chain_with_multiple_steps()

    print("\n✅ Tous les tests d'intégration passés!")