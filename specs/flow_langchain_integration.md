# Flux : Intégration avec chaînes LangChain

## Description
Test de l'utilisation de ClaudeCodeChatModel dans des chaînes LangChain complexes.

## Flux
1. Créer un ClaudeCodeChatModel
2. Créer un ChatPromptTemplate avec système et humain
3. Construire une chaîne avec l'opérateur pipe (|)
4. Invoquer la chaîne avec des variables
5. Vérifier que la chaîne fonctionne correctement
6. Tester avec un OutputParser

## Cas d'usage testés
- Chaîne simple prompt | model
- Chaîne avec parser prompt | model | parser
- Chaîne avec mémoire (ConversationBufferMemory)
- Utilisation dans un agent ReAct

## Validation
- Les chaînes s'exécutent sans erreur
- Les variables sont correctement substituées
- Les parsers fonctionnent
- L'intégration LCEL est complète