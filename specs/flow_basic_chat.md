# Flux : Chat Basique avec ClaudeCodeChatModel

## Description
Test de l'intégration basique du modèle Claude Code dans LangChain.

## Flux
1. Créer une instance de ClaudeCodeChatModel
2. Envoyer un message simple "Bonjour, qui es-tu?"
3. Recevoir et valider la réponse
4. Vérifier que le message de réponse est de type AIMessage
5. Confirmer que le contenu n'est pas vide

## Validation
- Le modèle répond correctement
- La réponse est un AIMessage valide
- Le contenu contient du texte
- Pas d'erreurs durant l'exécution