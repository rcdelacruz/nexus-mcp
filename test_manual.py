#!/usr/bin/env python3
"""
Manual integration test for Nexus MCP Server.
This script tests the actual functionality of the tools without mocking.
"""
import asyncio
from nexus_server import nexus_search, nexus_read


async def main():
    print("=" * 60)
    print("NEXUS MCP SERVER - MANUAL INTEGRATION TEST")
    print("=" * 60)
    print()

    # Test 1: Search in general mode
    print("Test 1: General web search")
    print("-" * 60)
    result = await nexus_search(
        query="Python programming language",
        mode="general",
        max_results=3
    )
    print(f"Results:\n{result[:500]}...")
    print()

    # Test 2: Search in docs mode
    print("Test 2: Documentation-focused search")
    print("-" * 60)
    result = await nexus_search(
        query="Python asyncio",
        mode="docs",
        max_results=2
    )
    print(f"Results:\n{result[:500]}...")
    print()

    # Test 3: Read a URL in general mode
    print("Test 3: Read URL in general mode")
    print("-" * 60)
    result = await nexus_read(
        url="https://example.com",
        focus="general"
    )
    print(f"Content length: {len(result)} characters")
    print(f"First 300 chars:\n{result[:300]}...")
    print()

    # Test 4: Read a URL with auto-detection
    print("Test 4: Read URL with auto-detection (technical site)")
    print("-" * 60)
    result = await nexus_read(
        url="https://docs.python.org/3/library/asyncio.html",
        focus="auto"
    )
    print(f"Content length: {len(result)} characters")
    print(f"Mode detected: {'CODE' if 'CODE' in result else 'GENERAL'}")
    print(f"First 300 chars:\n{result[:300]}...")
    print()

    # Test 5: Error handling - invalid mode
    print("Test 5: Error handling (invalid search mode)")
    print("-" * 60)
    result = await nexus_search(
        query="test",
        mode="invalid_mode"
    )
    print(f"Result: {result}")
    print()

    # Test 6: Error handling - empty query
    print("Test 6: Error handling (empty query)")
    print("-" * 60)
    result = await nexus_search(
        query="",
        mode="general"
    )
    print(f"Result: {result}")
    print()

    # Test 7: Error handling - invalid URL
    print("Test 7: Error handling (invalid URL)")
    print("-" * 60)
    result = await nexus_read(
        url="not-a-valid-url",
        focus="general"
    )
    print(f"Result: {result}")
    print()

    print("=" * 60)
    print("MANUAL INTEGRATION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
