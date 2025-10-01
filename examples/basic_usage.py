"""
Exemple d'utilisation de ClaudeCodeChatModel avec LangChain

Ce script montre comment utiliser Claude via votre abonnement Claude Code
pour prototyper des applications LangChain SANS frais API supplémentaires.
"""

import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

# Import de notre adaptateur
from claude_code_langchain import ClaudeCodeChatModel


def example_simple_invocation():
    """Exemple 1: Invocation simple du modèle"""
    print("\n📝 Exemple 1: Invocation Simple")
    print("-" * 40)

    # Créer le modèle (utilise votre abonnement Claude Code)
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.7,
        max_tokens=500
    )

    # Envoyer un message simple
    response = model.invoke([
        HumanMessage(content="Qu'est-ce que LangChain en 2 phrases?")
    ])

    print(f"Réponse: {response.content}")


def example_with_system_prompt():
    """Exemple 2: Utilisation avec prompt système"""
    print("\n🎯 Exemple 2: Avec Prompt Système")
    print("-" * 40)

    # Modèle avec configuration système
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        system_prompt="Tu es un expert Python qui répond de manière très concise.",
        temperature=0.3,
        max_tokens=200
    )

    # Messages avec contexte système
    messages = [
        SystemMessage(content="Utilise des exemples de code quand c'est pertinent"),
        HumanMessage(content="Comment créer une liste en Python?")
    ]

    response = model.invoke(messages)
    print(f"Réponse: {response.content}")


def example_streaming():
    """Exemple 3: Streaming de réponses"""
    print("\n🌊 Exemple 3: Streaming")
    print("-" * 40)

    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.8
    )

    print("Streaming de la réponse: ", end="")
    for chunk in model.stream([
        HumanMessage(content="Raconte une très courte histoire sur un robot")
    ]):
        print(chunk.content, end="", flush=True)
    print()  # Nouvelle ligne à la fin


def example_langchain_chain():
    """Exemple 4: Chaîne LangChain complète"""
    print("\n🔗 Exemple 4: Chaîne LangChain")
    print("-" * 40)

    # Créer les composants de la chaîne
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.5
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Tu es un assistant expert en {domain}"),
        ("human", "{question}")
    ])

    # Construire la chaîne avec LCEL
    chain = prompt | model | StrOutputParser()

    # Invoquer la chaîne
    response = chain.invoke({
        "domain": "intelligence artificielle",
        "question": "Qu'est-ce qu'un réseau de neurones?"
    })

    print(f"Réponse: {response}")


async def example_async_operations():
    """Exemple 5: Opérations asynchrones"""
    print("\n⚡ Exemple 5: Opérations Asynchrones")
    print("-" * 40)

    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.6
    )

    # Invocation asynchrone
    response = await model.ainvoke([
        HumanMessage(content="Qu'est-ce que Python async/await?")
    ])

    print(f"Réponse async: {response.content[:200]}...")

    # Streaming asynchrone
    print("\nStreaming async: ", end="")
    async for chunk in model.astream([
        HumanMessage(content="Liste 3 avantages de l'async")
    ]):
        print(".", end="", flush=True)
    print(" Terminé!")


def example_batch_processing():
    """Exemple 6: Traitement par batch"""
    print("\n📦 Exemple 6: Traitement Batch")
    print("-" * 40)

    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.4,
        max_tokens=100
    )

    # Plusieurs questions en batch
    questions = [
        [HumanMessage(content="Capitale de la France?")],
        [HumanMessage(content="Capitale de l'Espagne?")],
        [HumanMessage(content="Capitale de l'Italie?")]
    ]

    responses = model.batch(questions)

    for i, response in enumerate(responses, 1):
        print(f"Question {i}: {response.content}")


def example_complex_agent_chain():
    """Exemple 7: Chaîne d'agent complexe"""
    print("\n🤖 Exemple 7: Chaîne Complexe (Agent-like)")
    print("-" * 40)

    from langchain_core.runnables import RunnablePassthrough

    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.5
    )

    # Première étape: Analyser l'intention
    intent_prompt = ChatPromptTemplate.from_messages([
        ("system", "Détermine si la question est technique ou générale"),
        ("human", "{question}")
    ])

    # Deuxième étape: Répondre selon l'intention
    response_prompt = ChatPromptTemplate.from_messages([
        ("system", "Réponds à cette question {intent}"),
        ("human", "{question}")
    ])

    # Chaîne d'analyse d'intention
    intent_chain = intent_prompt | model | StrOutputParser()

    # Chaîne complète avec routing
    def route_response(inputs):
        intent = intent_chain.invoke({"question": inputs["question"]})
        return {
            "intent": "de manière technique" if "technique" in intent.lower() else "simplement",
            "question": inputs["question"]
        }

    full_chain = (
        RunnablePassthrough()
        | route_response
        | response_prompt
        | model
        | StrOutputParser()
    )

    response = full_chain.invoke({
        "question": "Comment fonctionne une API REST?"
    })

    print(f"Réponse adaptée: {response[:200]}...")


def example_continuous_session():
    """Exemple 8: Conversation multi-tour (gestion manuelle du contexte)"""
    print("\n💭 Exemple 8: Conversation Multi-Tour")
    print("-" * 40)

    # ClaudeCodeChatModel est STATELESS par design (compatible LangChain)
    # Pour maintenir le contexte, passer explicitement l'historique
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.6
    )

    print("Note: Le modèle est stateless (recommandé pour LangChain)")
    print("Le contexte est géré en passant l'historique explicitement")

    # Construire l'historique manuellement
    conversation = []

    # Première interaction
    conversation.append(HumanMessage(content="Je m'appelle Alice"))
    response1 = model.invoke(conversation)
    print(f"R1: {response1.content}")

    # Ajouter la réponse à l'historique
    conversation.append(response1)

    # Deuxième interaction avec contexte
    conversation.append(HumanMessage(content="Quel est mon nom?"))
    response2 = model.invoke(conversation)
    print(f"R2: {response2.content}")
    print("\nContexte maintenu via historique explicite ✓")


def main():
    """Fonction principale pour exécuter tous les exemples"""
    print("=" * 50)
    print("🚀 Exemples ClaudeCodeChatModel pour LangChain")
    print("=" * 50)
    print("\nUtilise votre abonnement Claude Code (20$/mois)")
    print("AUCUN frais API supplémentaire!")

    # Exécuter les exemples synchrones
    example_simple_invocation()
    example_with_system_prompt()
    example_streaming()
    example_langchain_chain()
    example_batch_processing()
    example_complex_agent_chain()

    # Exécuter les exemples asynchrones
    print("\n" + "=" * 50)
    print("Exemples Asynchrones")
    print("=" * 50)
    asyncio.run(example_async_operations())

    # Session continue (optionnel)
    example_continuous_session()

    print("\n" + "=" * 50)
    print("✅ Tous les exemples exécutés avec succès!")
    print("=" * 50)
    print("\n💡 Astuce: Remplacez ClaudeCodeChatModel par ChatAnthropic")
    print("   quand vous serez prêt pour la production avec l'API officielle!")


if __name__ == "__main__":
    main()