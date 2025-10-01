# Flow: Basic Chat with ClaudeCodeChatModel

## Description
Test of basic Claude Code model integration in LangChain.

## Flow
1. Create a ClaudeCodeChatModel instance
2. Send a simple message "Hello, who are you?"
3. Receive and validate the response
4. Verify that the response message is of type AIMessage
5. Confirm that the content is not empty

## Validation
- The model responds correctly
- The response is a valid AIMessage
- The content contains text
- No errors during execution
