#!/usr/bin/env python3
"""
Simple MCP client for testing the music MCP server.
This script sends MCP protocol messages and displays responses.
"""

import asyncio
import json
import sys
from typing import Dict, Any

async def test_mcp_server():
    """Test the MCP server by running it and sending test messages."""

    # Import the server module
    import server

    # Create a mock stdin/stdout for testing
    from io import StringIO
    import threading
    import queue

    # We'll run the server in a separate thread and communicate via queues
    request_queue = queue.Queue()
    response_queue = queue.Queue()

    class MockStream:
        def __init__(self, input_queue, output_queue):
            self.input_queue = input_queue
            self.output_queue = output_queue

        async def read(self):
            # Wait for a message from the input queue
            while True:
                try:
                    message = self.input_queue.get_nowait()
                    return message
                except queue.Empty:
                    await asyncio.sleep(0.1)

        async def write(self, message):
            self.output_queue.put(message)

    # Create mock streams
    mock_read_stream = MockStream(request_queue, response_queue)
    mock_write_stream = MockStream(response_queue, request_queue)

    # Start the server in a separate task
    async def run_server():
        try:
            await server.server.run(
                mock_read_stream,
                mock_write_stream,
                server.server.create_initialization_options()
            )
        except Exception as e:
            print(f"Server error: {e}")

    server_task = asyncio.create_task(run_server())

    # Wait a bit for server to start
    await asyncio.sleep(1)

    # Test messages
    test_messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
    ]

    print("Testing MCP Server...")
    print("=" * 50)

    for i, message in enumerate(test_messages):
        print(f"\nTest {i+1}: {message['method']}")
        print(f"Request: {json.dumps(message, indent=2)}")

        # Send message to server
        request_queue.put(json.dumps(message).encode() + b'\n')

        # Wait for response
        try:
            response_data = await asyncio.wait_for(mock_read_stream.read(), timeout=5.0)
            response = json.loads(response_data.decode())
            print(f"Response: {json.dumps(response, indent=2)}")
        except asyncio.TimeoutError:
            print("Timeout waiting for response")
        except Exception as e:
            print(f"Error: {e}")

    # Clean up
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(test_mcp_server())