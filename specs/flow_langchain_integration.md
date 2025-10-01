# Flow: Integration with LangChain Chains

## Description
Test of ClaudeCodeChatModel usage in complex LangChain chains.

## Flow
1. Create a ClaudeCodeChatModel
2. Create a ChatPromptTemplate with system and human messages
3. Build a chain with the pipe operator (|)
4. Invoke the chain with variables
5. Verify that the chain works correctly
6. Test with an OutputParser

## Test Cases
- Simple chain: prompt | model
- Chain with parser: prompt | model | parser
- Chain with memory (ConversationBufferMemory)
- Usage in a ReAct agent

## Validation
- Chains execute without errors
- Variables are correctly substituted
- Parsers work as expected
- LCEL integration is complete
