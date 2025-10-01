"""
Flow test: Integration with LangChain chains
"""

import asyncio

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def test_simple_chain():
    """Test of a simple chain with prompt and model"""
    from claude_code_langchain import ClaudeCodeChatModel

    # Create components
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.5, max_tokens=200)

    prompt = ChatPromptTemplate.from_messages(
        [("system", "You are an assistant that responds about {language}"), ("human", "{question}")]
    )

    # Create the chain
    chain = prompt | model

    try:
        # Invoke the chain
        response = chain.invoke({"language": "Python", "question": "What is a list comprehension?"})

        # Validate
        assert response is not None
        assert len(response.content) > 0

        print("✅ Simple chain test passed")
        print(f"   Response: {response.content[:100]}...")

    except Exception as e:
        pytest.fail(f"Simple chain test failed: {e}")


def test_chain_with_parser():
    """Test of a chain with output parser"""
    from claude_code_langchain import ClaudeCodeChatModel

    # Create components
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.3, max_tokens=150)

    prompt = ChatPromptTemplate.from_messages(
        [("system", "Always respond very concisely"), ("human", "{input}")]
    )

    parser = StrOutputParser()

    # Create complete chain
    chain = prompt | model | parser

    try:
        # Invoke the chain
        response = chain.invoke({"input": "Define Python in 5 words maximum"})

        # Validate parsed string
        assert isinstance(response, str)
        assert len(response) > 0

        print("✅ Chain with parser test passed")
        print(f"   Parsed response: {response}")

    except Exception as e:
        pytest.fail(f"Parser test failed: {e}")


@pytest.mark.asyncio
async def test_async_chain():
    """Test of an asynchronous chain"""
    from claude_code_langchain import ClaudeCodeChatModel

    # Create components
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.7)

    prompt = ChatPromptTemplate.from_messages(
        [("system", "You are an expert in {domain}"), ("human", "Explain {concept}")]
    )

    chain = prompt | model | StrOutputParser()

    try:
        # Invoke asynchronously
        response = await chain.ainvoke({"domain": "computer science", "concept": "algorithms"})

        # Validate
        assert isinstance(response, str)
        assert len(response) > 0

        print("✅ Async chain test passed")
        print(f"   Response: {response[:100]}...")

    except Exception as e:
        pytest.fail(f"Async test failed: {e}")


def test_batch_processing():
    """Test of batch processing"""
    from claude_code_langchain import ClaudeCodeChatModel

    # Create model
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.5, max_tokens=100)

    # Create multiple messages
    batch_inputs = [
        [HumanMessage(content="What is 2+2?")],
        [HumanMessage(content="Capital of France?")],
        [HumanMessage(content="Color of the sky?")],
    ]

    try:
        # Process batch
        responses = model.batch(batch_inputs)

        # Validate
        assert len(responses) == 3
        for response in responses:
            assert response is not None
            assert len(response.content) > 0

        print("✅ Batch test passed")
        print(f"   {len(responses)} responses received")

    except Exception as e:
        pytest.fail(f"Batch test failed: {e}")


def test_streaming_chain():
    """Test of streaming in a chain"""
    from claude_code_langchain import ClaudeCodeChatModel

    # Create components
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.7)

    prompt = ChatPromptTemplate.from_messages([("human", "Tell a short story about {topic}")])

    chain = prompt | model

    try:
        # Stream the response
        chunks_count = 0
        for chunk in chain.stream({"topic": "a robot"}):
            chunks_count += 1
            print(".", end="", flush=True)

        print()  # New line
        assert chunks_count > 0

        print("✅ Streaming chain test passed")
        print(f"   {chunks_count} chunks streamed")

    except Exception as e:
        pytest.fail(f"Streaming test failed: {e}")


def test_complex_chain_with_multiple_steps():
    """Test of a complex chain with multiple steps"""
    from langchain_core.runnables import RunnablePassthrough

    from claude_code_langchain import ClaudeCodeChatModel

    # Create model
    model = ClaudeCodeChatModel(model="claude-sonnet-4-20250514", temperature=0.5, max_tokens=150)

    # First step: classify
    classify_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Classify the following text as 'positive', 'negative', or 'neutral'"),
            ("human", "{text}"),
        ]
    )

    # Second step: respond based on classification
    response_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "The sentiment is {sentiment}. Respond appropriately."),
            ("human", "How to react to: {text}"),
        ]
    )

    # Complex chain
    classify_chain = classify_prompt | model | StrOutputParser()

    def create_response_input(inputs):
        sentiment = classify_chain.invoke({"text": inputs["text"]})
        return {"sentiment": sentiment, "text": inputs["text"]}

    complex_chain = (
        RunnablePassthrough.assign(sentiment=lambda x: classify_chain.invoke({"text": x["text"]}))
        | response_prompt
        | model
        | StrOutputParser()
    )

    try:
        # Test with a text
        response = complex_chain.invoke({"text": "This product is absolutely fantastic!"})

        # Validate
        assert isinstance(response, str)
        assert len(response) > 0

        print("✅ Complex chain test passed")
        print(f"   Response: {response[:150]}...")

    except Exception as e:
        pytest.fail(f"Complex chain test failed: {e}")


if __name__ == "__main__":
    # Run the tests
    print("🧪 LangChain Integration Tests\n")

    print("1. Testing simple chain...")
    test_simple_chain()

    print("\n2. Testing with parser...")
    test_chain_with_parser()

    print("\n3. Testing async...")
    asyncio.run(test_async_chain())

    print("\n4. Testing batch processing...")
    test_batch_processing()

    print("\n5. Testing chain streaming...")
    test_streaming_chain()

    print("\n6. Testing complex chain...")
    test_complex_chain_with_multiple_steps()

    print("\n✅ All integration tests passed!")
