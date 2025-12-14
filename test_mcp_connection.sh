#!/bin/bash

echo "=========================================="
echo "NEXUS MCP SERVER - CONNECTION TEST"
echo "=========================================="
echo ""

echo "1. Checking MCP server status..."
claude mcp list | grep nexus
echo ""

echo "2. Getting server details..."
claude mcp get nexus
echo ""

echo "3. Testing if server accepts MCP protocol..."
echo "   (The server should respond to MCP initialization)"
echo ""

# Test the server directly with a simple stdin/stdout test
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}},"id":1}' | \
/Users/ronalddelacruz/Projects/stratpoint/nexus-mcp/.venv/bin/python \
/Users/ronalddelacruz/Projects/stratpoint/nexus-mcp/nexus_server.py 2>&1 | head -5

echo ""
echo "=========================================="
echo "If you see JSON-RPC response above, the MCP server is working!"
echo "=========================================="
