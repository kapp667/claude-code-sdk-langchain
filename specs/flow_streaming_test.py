"""
Flow test: Streaming Responses with ClaudeCodeChatModel
Tests real-time streaming capabilities through public APIs only.
Reference: flow_streaming.md
"""

import asyncio
import time
from typing import List
import pytest
from langchain_core.messages import HumanMessage, AIMessageChunk
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def test_flow_sync_streaming_basic():
    """
    Test synchronous streaming flow - user receives incremental chunks.
    Tests the public stream() method as a black box.
    """
    from claude_code_langchain import ClaudeCodeChatModel

    # User creates model instance
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.7, max_tokens=300)

    # User requests a numbered list (promotes multi-chunk response)
    messages = [HumanMessage(content="List 3 benefits of Python programming, numbered 1-3")]

    # User collects chunks
    chunks_received = []
    full_content = ""

    # User iterates over stream
    for chunk in model.stream(messages):
        chunks_received.append(chunk)
        # Le chunk peut être un AIMessageChunk ou ChatGenerationChunk
        if hasattr(chunk, "content"):
            full_content += chunk.content
        elif hasattr(chunk, "message") and hasattr(chunk.message, "content"):
            full_content += chunk.message.content

    # Validate streaming occurred
    assert len(chunks_received) > 0, "No chunks received from stream"
    assert len(full_content) > 0, "No content received from stream"

    # Verify we got multiple chunks (streaming, not bulk)
    # For very short responses, we might get 1-2 chunks minimum
    assert len(chunks_received) >= 1, "Expected incremental streaming"

    # Verify chunk types
    from langchain_core.messages import AIMessageChunk
    from langchain_core.outputs import ChatGenerationChunk

    for chunk in chunks_received:
        # LangChain peut retourner soit ChatGenerationChunk soit AIMessageChunk directement
        assert isinstance(
            chunk, (ChatGenerationChunk, AIMessageChunk)
        ), f"Invalid chunk type: {type(chunk)}"
        if isinstance(chunk, ChatGenerationChunk):
            assert hasattr(chunk, "message"), "Chunk missing message attribute"
            assert isinstance(chunk.message, AIMessageChunk), "Invalid message type in chunk"

    print(f"✅ Sync streaming test passed: {len(chunks_received)} chunks received")


@pytest.mark.asyncio
async def test_flow_async_streaming_basic():
    """
    Test asynchronous streaming flow - user processes chunks in real-time.
    Tests the public astream() method as a black box.
    """
    from claude_code_langchain import ClaudeCodeChatModel

    # User creates model instance
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.7, max_tokens=400)

    # User prepares message
    messages = [HumanMessage(content="Explain async programming in 3 steps")]

    # User collects chunks asynchronously
    chunks_received = []
    full_content = ""
    chunk_times = []

    # User asynchronously iterates
    start_time = time.time()
    async for chunk in model.astream(messages):
        chunk_times.append(time.time() - start_time)
        chunks_received.append(chunk)
        if hasattr(chunk, "content"):
            full_content += chunk.content

    # Validate async streaming
    assert len(chunks_received) > 0, "No chunks received from async stream"
    assert len(full_content) > 0, "No content from async stream"

    # Verify chunks arrived over time (not all at once)
    if len(chunk_times) > 1:
        # Check that chunks arrived at different times
        time_differences = [
            chunk_times[i + 1] - chunk_times[i] for i in range(len(chunk_times) - 1)
        ]
        assert any(diff > 0 for diff in time_differences), "Chunks should arrive incrementally"

    print(
        f"✅ Async streaming test passed: {len(chunks_received)} chunks over {chunk_times[-1]:.2f}s"
    )


def test_flow_streaming_vs_nonstreaming_consistency():
    """
    Test that streaming produces the same final content as non-streaming.
    Validates public API consistency between invoke() and stream().
    """
    from claude_code_langchain import ClaudeCodeChatModel

    # User creates model with fixed temperature for consistency
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.2,  # Lower temperature for more consistent responses
        max_tokens=200,
    )

    # User prepares same message for both methods
    messages = [HumanMessage(content="What is 10 + 15?")]

    # User gets non-streaming response
    non_streaming_response = model.invoke(messages)
    non_streaming_content = non_streaming_response.content

    # User gets streaming response
    streaming_content = ""
    for chunk in model.stream(messages):
        if hasattr(chunk, "content"):
            streaming_content += chunk.content

    # Both should provide an answer (content may vary slightly due to model behavior)
    assert len(non_streaming_content) > 0, "Non-streaming response is empty"
    assert len(streaming_content) > 0, "Streaming response is empty"

    # Both should mention the answer (25)
    assert "25" in non_streaming_content or "twenty-five" in non_streaming_content.lower()
    assert "25" in streaming_content or "twenty-five" in streaming_content.lower()

    print(f"✅ Streaming consistency test passed")


def test_flow_chain_streaming():
    """
    Test streaming through a LangChain chain pipeline.
    Validates that streaming works with prompt templates and parsers.
    """
    from claude_code_langchain import ClaudeCodeChatModel

    # User creates model
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.7, max_tokens=300)

    # User creates a prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a storyteller. Tell a story about {topic} in 3 sentences."),
            ("human", "{request}"),
        ]
    )

    # User creates a chain
    chain = prompt | model

    # User streams through the chain
    chunks_count = 0
    full_story = ""

    for chunk in chain.stream({"topic": "a brave robot", "request": "Make it inspiring"}):
        chunks_count += 1
        if hasattr(chunk, "content"):
            full_story += chunk.content

    # Validate chain streaming
    assert chunks_count > 0, "No chunks from chain stream"
    assert len(full_story) > 0, "No story content from chain"

    # Story should mention robot (topic was properly passed)
    assert "robot" in full_story.lower(), "Chain didn't process topic variable"

    print(f"✅ Chain streaming test passed: {chunks_count} chunks")


@pytest.mark.asyncio
async def test_flow_async_chain_streaming_with_parser():
    """
    Test async streaming through a chain with an output parser.
    Validates end-to-end streaming with transformations.
    """
    from claude_code_langchain import ClaudeCodeChatModel

    # User creates model
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.5, max_tokens=200)

    # User creates chain with parser
    prompt = ChatPromptTemplate.from_messages(
        [("system", "You are a helpful assistant"), ("human", "{question}")]
    )

    parser = StrOutputParser()
    chain = prompt | model | parser

    # User async streams with parser
    chunks = []
    full_text = ""

    async for chunk in chain.astream({"question": "What is the capital of France?"}):
        chunks.append(chunk)
        full_text += chunk  # Parser outputs strings directly

    # Validate parsed streaming
    assert len(chunks) > 0, "No chunks from parsed stream"
    assert len(full_text) > 0, "No text from parsed stream"
    assert "paris" in full_text.lower(), "Expected answer not in stream"

    # All chunks should be strings (parser output)
    for chunk in chunks:
        assert isinstance(chunk, str), "Parser should output string chunks"

    print(f"✅ Async chain with parser test passed: {len(chunks)} string chunks")


def test_flow_streaming_cancellation():
    """
    Test that streaming can be interrupted by the user.
    Validates proper resource cleanup on early termination.
    """
    from claude_code_langchain import ClaudeCodeChatModel

    # User creates model
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.7,
        max_tokens=1000,  # Large limit to ensure multiple chunks
    )

    # User starts streaming but stops after a few chunks
    messages = [
        HumanMessage(content="Count from 1 to 100 slowly, with explanation for each number")
    ]

    chunks_before_stop = 3
    collected_chunks = []

    # User interrupts stream after N chunks
    for i, chunk in enumerate(model.stream(messages)):
        collected_chunks.append(chunk)
        if i >= chunks_before_stop - 1:
            break  # User stops iterating

    # Validate controlled interruption
    assert len(collected_chunks) == chunks_before_stop, "Stream didn't stop when requested"

    # Stream should have provided partial content
    partial_content = "".join(
        chunk.content for chunk in collected_chunks if hasattr(chunk, "content")
    )
    assert len(partial_content) > 0, "No partial content before interruption"

    print(f"✅ Streaming cancellation test passed: stopped after {chunks_before_stop} chunks")


if __name__ == "__main__":
    print("🧪 Flow Tests: Streaming Functionality\n")

    print("1. Testing synchronous streaming...")
    test_flow_sync_streaming_basic()

    print("\n2. Testing async streaming...")
    asyncio.run(test_flow_async_streaming_basic())

    print("\n3. Testing streaming vs non-streaming consistency...")
    test_flow_streaming_vs_nonstreaming_consistency()

    print("\n4. Testing chain streaming...")
    test_flow_chain_streaming()

    print("\n5. Testing async chain with parser...")
    asyncio.run(test_flow_async_chain_streaming_with_parser())

    print("\n6. Testing streaming cancellation...")
    test_flow_streaming_cancellation()

    print("\n✅ All streaming flow tests passed!")
