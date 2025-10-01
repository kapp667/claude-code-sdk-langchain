#!/usr/bin/env python3
"""
Ultra-simple test to verify the adapter works
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🧪 Simple ClaudeCodeChatModel Test\n")
    print("=" * 50)

    # 1. Import
    print("1️⃣  Importing module...")
    from claude_code_langchain import ClaudeCodeChatModel
    from langchain_core.messages import HumanMessage
    print("   ✅ Import successful")

    # 2. Model creation
    print("\n2️⃣  Creating model...")
    model = ClaudeCodeChatModel(
        model="claude-sonnet-4-20250514",
        temperature=0.5,
        max_tokens=100
    )
    print("   ✅ Model created")

    # 3. Simple invocation test
    print("\n3️⃣  Testing invocation...")
    print("   Question: 'What is 2+2?'")

    response = model.invoke([
        HumanMessage(content="What is 2+2?")
    ])

    print(f"   ✅ Response received: {response.content}")

    # 4. Response type verification
    print("\n4️⃣  Verifying response type...")
    from langchain_core.messages import AIMessage
    assert isinstance(response, AIMessage), "Response is not an AIMessage"
    assert len(response.content) > 0, "Response is empty"
    print("   ✅ Correct type (AIMessage)")

    print("\n" + "=" * 50)
    print("🎉 TEST PASSED! The adapter works!")
    print("=" * 50)

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\n💡 Make sure that:")
    print("   1. claude-code-sdk is installed: pip install claude-code-sdk")
    print("   2. langchain is installed: pip install langchain langchain-core")
    print("   3. Claude Code CLI is installed: npm install -g @anthropic-ai/claude-code")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Error during test: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
