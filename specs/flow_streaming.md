# Flow: Streaming Responses with ClaudeCodeChatModel

## Description
Validates real-time streaming capabilities of the Claude Code adapter, both synchronous and asynchronous, ensuring users receive incremental responses as they are generated.

## User Journey

### Synchronous Streaming Flow
1. User creates a ClaudeCodeChatModel instance
2. User calls model.stream() with a message asking for a numbered list
3. User iterates over the stream to receive chunks
4. User collects all chunks to form the complete response
5. User verifies chunks arrive incrementally (not all at once)

### Asynchronous Streaming Flow
1. User creates a ClaudeCodeChatModel instance
2. User calls model.astream() with a message in an async context
3. User asynchronously iterates over chunks
4. User processes each chunk as it arrives (e.g., display to UI)
5. User handles the complete response when streaming ends

### LangChain Chain Streaming Flow
1. User creates a prompt template and model chain
2. User calls chain.stream() with input variables
3. User receives streamed chunks through the chain pipeline
4. User applies transformations or parsers to streaming output
5. User handles both content and metadata from chunks

## Expected Behavior
- Chunks arrive incrementally, not in bulk
- Each chunk contains partial content
- Streaming maintains message coherence
- Final assembled message matches non-streaming response
- Metadata (if present) is preserved in chunks
- Stream can be interrupted/cancelled by user

## Success Criteria
- At least 2 chunks received for multi-sentence responses
- Total streamed content equals non-streamed response
- No data loss or corruption during streaming
- Proper async/await handling without deadlocks
- Chain streaming preserves all transformations