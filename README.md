# 🌐 Nexus MCP Server

> **The Hybrid Search & Retrieval Engine for AI Agents.**

Nexus is a local Model Context Protocol (MCP) server that combines the best features of **Exa** (semantic web search) and **Ref** (documentation-optimized reading). It provides your AI agent (Claude, Cursor, etc.) with the ability to search the web and extract surgical, token-efficient context from documentation without requiring external API keys.

## ✨ Features

### 1. Hybrid Search (`nexus_search`)
Nexus understands that searching for news is different from searching for API docs.
*   **General Mode:** Performs broad web searches (like Exa) to find articles, news, and general information.
*   **Docs Mode:** Automatically filters results to prioritize technical domains (`readthedocs`, `github`, `stackoverflow`, official documentation).

### 2. Intelligent Reading (`nexus_read`)
Nexus doesn't just dump HTML into your context window. It parses content based on intent.
*   **General Focus:** Cleans articles, removing ads, navigation bars, and fluff. Perfect for reading news or blog posts.
*   **Code Focus:** Aggressively strips conversational text, retaining only **Headers**, **Code Blocks**, and **Tables**. This mimics `ref.tools`, ensuring your model gets pure syntax without the noise.
*   **Auto-Detect:** Automatically switches to "Code Focus" when visiting technical sites like GitHub or API references.

### 3. Privacy & Cost
*   **No API Keys Required:** Uses DuckDuckGo for search and standard HTTP requests for retrieval.
*   **Runs Locally:** Your data stays on your machine until the cleaned context is sent to the LLM.

---

## 🛠️ Installation

### Prerequisites
*   Python 3.10+
*   [`uv`](https://github.com/astral-sh/uv) (Recommended) or `pip`

### Quick Install

1. Clone or download this repository:
```bash
git clone https://github.com/rcdelacruz/nexus-mcp.git
cd nexus-mcp
```

2. Install using pip (with virtual environment recommended):
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

3. For development (includes testing tools):
```bash
pip install -e ".[dev]"
```

### Manual Installation
If installing dependencies manually:
```bash
pip install mcp httpx beautifulsoup4 ddgs
```

---

## ⚙️ Configuration

### Claude Code (CLI)

**Quick Setup:**
```bash
# Navigate to nexus-mcp directory
cd /path/to/nexus-mcp

# Install dependencies first
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Add the server to Claude Code
claude mcp add --transport stdio nexus --scope project -- \
  $(pwd)/.venv/bin/python $(pwd)/nexus_server.py

# Verify installation
claude mcp list
```

This creates `.mcp.json` in your project:
```json
{
  "mcpServers": {
    "nexus": {
      "type": "stdio",
      "command": "/absolute/path/to/nexus-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/nexus-mcp/nexus_server.py"]
    }
  }
}
```

**For portability, use environment variables:**
Edit `.mcp.json` manually:
```json
{
  "mcpServers": {
    "nexus": {
      "type": "stdio",
      "command": "${PWD}/.venv/bin/python",
      "args": ["${PWD}/nexus_server.py"]
    }
  }
}
```

**Check server status:**
```bash
claude mcp list        # Should show: ✓ Connected
/mcp                   # In conversation: shows available tools
```

**Scopes:**
- `--scope project` - Creates `.mcp.json` (shareable via git)
- `--scope local` - Personal config in `~/.claude.json`
- `--scope user` - Available across all projects

---

### Claude Desktop / Cursor

**Config Location:**
*   **MacOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
*   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Using uv (recommended):**
```json
{
  "mcpServers": {
    "nexus": {
      "command": "uv",
      "args": [
        "run",
        "--with", "mcp",
        "--with", "httpx",
        "--with", "beautifulsoup4",
        "--with", "ddgs",
        "/ABSOLUTE/PATH/TO/YOUR/nexus_server.py"
      ]
    }
  }
}
```

**Using virtual environment:**
```json
{
  "mcpServers": {
    "nexus": {
      "command": "/ABSOLUTE/PATH/TO/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/nexus_server.py"]
    }
  }
}
```

*Replace `/ABSOLUTE/PATH/TO/YOUR/` with the actual path.*

---

## 🚀 Usage

Once connected, simply prompt Claude naturally. Nexus handles the tool selection.

### Verify It's Working

Check server connection:
```bash
claude mcp list
# Should show: nexus - ✓ Connected

# In a Claude Code conversation:
/mcp
# Should show nexus with 2 tools available
```

See [VERIFICATION.md](VERIFICATION.md) for detailed testing instructions.

### Scenario 1: Technical Research (Ref Emulation)
> **User:** "How do I use `asyncio.gather` in Python? Check the docs."

*   **Nexus Action:**
    1.  Search: `nexus_search(query="python asyncio gather", mode="docs")`
    2.  Read: `nexus_read(url="docs.python.org/...", focus="code")`
*   **Result:** The AI receives only the function signature and code examples, saving context window space.

### Scenario 2: General Research (Exa Emulation)
> **User:** "Search for the latest updates on the NVIDIA Blackwell chip."

*   **Nexus Action:**
    1.  Search: `nexus_search(query="NVIDIA Blackwell updates", mode="general")`
    2.  Read: `nexus_read(url="techcrunch.com/...", focus="general")`
*   **Result:** The AI reads a clean, ad-free summary of the news article.

---

## 🧠 Architecture

Nexus is built on the [Model Context Protocol](https://modelcontextprotocol.io/) using the FastMCP Python SDK.

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **MCP Framework** | `FastMCP` | Server implementation and tool registration |
| **Search Backend** | `DDGS` (DuckDuckGo) | Free web search without API keys |
| **HTTP Client** | `httpx` | Async HTTP requests with timeout handling |
| **HTML Parsing** | `BeautifulSoup4` | Intelligent content extraction |
| **Doc Detection** | Heuristic URL matching | Auto-detection of technical sites |

### Production Features

✅ **Comprehensive Error Handling** - All edge cases covered with graceful fallbacks
✅ **Input Validation** - URL format, parameter bounds, and mode validation
✅ **Proper Logging** - Structured logging instead of print statements
✅ **Configurable Limits** - Timeouts, content length, and result counts
✅ **85% Test Coverage** - 19 comprehensive unit tests
✅ **Type Hints** - Full type annotations for better IDE support
✅ **Dependency Management** - Modern pyproject.toml configuration

---

## 🧪 Testing

Run the test suite:
```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_nexus_server.py -v

# Run manual integration test
python test_manual.py
```

---

## 📊 Project Structure

```
nexus-mcp/
├── nexus_server.py      # Main MCP server implementation
├── tests/               # Comprehensive test suite
│   ├── __init__.py
│   └── test_nexus_server.py
├── test_manual.py       # Manual integration testing
├── pyproject.toml       # Project configuration & dependencies
├── LICENSE              # MIT License
├── README.md            # This file
└── .gitignore          # Git ignore rules
```

---

## 🤝 Contributing

Contributions are welcome! Please ensure:
- All tests pass (`pytest`)
- Code coverage remains above 80%
- Follow existing code style and patterns
- Add tests for new features

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details. Free to use and modify.
