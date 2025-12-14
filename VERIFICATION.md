# How to Verify Nexus MCP Server is Working

## ✅ Server Connection Verified

The MCP server is **successfully connected** to Claude Code:

```bash
$ claude mcp list
nexus: ... - ✓ Connected
```

Server info confirmed:
- **Name**: Nexus-Hybrid-Search
- **Version**: 1.24.0
- **Protocol**: 2024-11-05
- **Tools Available**: 2 (nexus_search, nexus_read)

## 🧪 How to Test in a New Claude Code Conversation

### Method 1: Ask Claude Code to Use the Tools

Start a new conversation and try:

```
Search for "Python asyncio documentation" and read the first result
```

Claude Code should automatically:
1. Use `nexus_search` to find results
2. Use `nexus_read` to extract content
3. Summarize the information for you

### Method 2: Use /mcp Command

In a Claude Code conversation, type:

```
/mcp
```

You should see:
```
Connected MCP Servers:
- nexus (2 tools)
  - nexus_search
  - nexus_read
```

### Method 3: Explicitly Request Tool Usage

Ask Claude Code:

```
Use the nexus_search tool to search for "FastAPI tutorial"
```

Then:

```
Use the nexus_read tool to read https://docs.python.org
```

## 🎯 What Success Looks Like

**Search Results** should show:
- Title
- URL
- Snippet
- Formatted nicely

**Read Results** should show:
- Clean extracted content
- Headers and code blocks (for docs mode)
- No navigation junk or ads

## 🔍 Debugging

If tools don't work:

1. **Check server status:**
   ```bash
   claude mcp list
   ```

2. **Restart Claude Code** (MCP connections require restart)

3. **Check logs:**
   ```bash
   cat ~/.local/state/claude/logs/mcp-*.log
   ```

4. **Verify manually:**
   ```bash
   ./test_mcp_connection.sh
   ```

## 📊 Expected Tool Behavior

### nexus_search
- **Input**: query (string), mode ("general" or "docs"), max_results (1-20)
- **Output**: Formatted list of search results with titles, URLs, snippets
- **Example**: Search for Python libraries

### nexus_read
- **Input**: url (string), focus ("auto", "general", or "code")
- **Output**: Clean, extracted webpage content
- **Example**: Read technical documentation

## ✨ The Tools Are Working If...

- ✅ `claude mcp list` shows "✓ Connected"
- ✅ Server responds to JSON-RPC protocol
- ✅ Tools appear in `/mcp` command
- ✅ Claude Code can call the tools in conversations
- ✅ Results are properly formatted and returned
