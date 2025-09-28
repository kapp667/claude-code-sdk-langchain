# Flow: Session Management with ClaudeCodeChatModel

## Description
Validates the continuous session capabilities of the Claude Code adapter, allowing users to maintain context across multiple interactions.

## User Journey

### Single-Turn Session Flow (Default)
1. User creates ClaudeCodeChatModel without session configuration
2. User sends first message and receives response
3. User sends second message (new context)
4. System treats each invocation independently
5. No context is retained between invocations

### Continuous Session Flow
1. User creates ClaudeCodeChatModel with `use_continuous_session=True`
2. User connects to establish session
3. User sends first message, establishing context
4. User sends follow-up message referring to previous context
5. Model remembers and uses previous conversation
6. User disconnects when done
7. Session context is cleared

### Context Manager Session Flow
1. User creates model with continuous session enabled
2. User enters async context manager (`async with model`)
3. Session automatically connects
4. User conducts multi-turn conversation
5. Session automatically disconnects on context exit
6. Resources are properly cleaned up

### Session Recovery Flow
1. User has active continuous session
2. Session unexpectedly disconnects (network issue)
3. User detects disconnection
4. User reconnects to continue session
5. Conversation continues (context may be lost depending on implementation)

### Multiple Concurrent Sessions Flow
1. User creates multiple ClaudeCodeChatModel instances
2. Each instance maintains independent session
3. User interacts with different sessions in parallel
4. Each session maintains its own context
5. Sessions don't interfere with each other

## Expected Behavior

### Single-Turn Mode
- Each invoke() is independent
- No memory between calls
- Suitable for stateless operations
- Lower resource usage

### Continuous Session Mode
- Context preserved across invocations
- Can reference previous messages
- Maintains conversation history
- Requires explicit connection/disconnection
- Higher resource usage but better for conversations

## Success Criteria
- Single-turn mode has no context leakage
- Continuous sessions maintain context correctly
- Context manager properly manages lifecycle
- Disconnection is handled gracefully
- Multiple sessions work independently
- No resource leaks after session cleanup