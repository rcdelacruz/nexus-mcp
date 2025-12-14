import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import httpx
import bs4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MAX_RESULTS = 5
MAX_CONTENT_LENGTH = 8000
MIN_CODE_ELEMENTS_THRESHOLD = 5
REQUEST_TIMEOUT = 15.0
SEARCH_TIMEOUT = 30.0

# Initialize the "Nexus" Server
mcp = FastMCP("Nexus-Hybrid-Search")

@mcp.tool()
async def nexus_search(
    query: str,
    mode: str = "general",
    max_results: int = DEFAULT_MAX_RESULTS
) -> str:
    """
    A hybrid search tool combining Exa's breadth and Ref's specificity.

    Args:
        query: The search term.
        mode: 'general' for broad web search (Exa style).
              'docs' to prioritize technical documentation (Ref style).
        max_results: Number of results to return (1-20).

    Returns:
        Formatted search results with titles, URLs, and snippets.
    """
    logger.info(f"Search requested - Query: '{query}', Mode: {mode}, Max results: {max_results}")

    # Validate inputs
    if not query or not query.strip():
        error_msg = "Query cannot be empty"
        logger.error(error_msg)
        return f"Error: {error_msg}"

    if mode not in ["general", "docs"]:
        error_msg = f"Invalid mode '{mode}'. Must be 'general' or 'docs'"
        logger.error(error_msg)
        return f"Error: {error_msg}"

    # Clamp max_results to reasonable range
    max_results = max(1, min(max_results, 20))

    # If 'docs' mode is selected, we modify the query to target technical sources
    final_query = query.strip()
    if mode == "docs":
        final_query += " site:readthedocs.io OR site:github.com OR site:stackoverflow.com OR documentation API"
        logger.debug(f"Enhanced query for docs mode: '{final_query}'")

    results = []
    try:
        # Use DuckDuckGo as our free backend
        with DDGS(timeout=SEARCH_TIMEOUT) as ddgs:
            # Convert generator to list to properly check if empty
            ddg_results = list(ddgs.text(final_query, max_results=max_results))

            if not ddg_results:
                logger.warning(f"No results found for query: '{query}'")
                return "No results found. Try a different query or mode."

            for r in ddg_results:
                title = r.get('title', 'No title')
                url = r.get('href', 'No URL')
                snippet = r.get('body', 'No description')
                results.append(f"- [Title]: {title}\n  [URL]: {url}\n  [Snippet]: {snippet}")

            logger.info(f"Search successful - Found {len(results)} results")
            return "\n\n".join(results)

    except TimeoutError:
        error_msg = "Search timed out. Please try again."
        logger.error(f"Search timeout for query: '{query}'")
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        logger.exception(f"Unexpected error during search: {query}")
        return f"Error: {error_msg}"

@mcp.tool()
async def nexus_read(url: str, focus: str = "auto") -> str:
    """
    Reads a URL with intelligent parsing logic.

    Args:
        url: The URL to visit.
        focus:
            'general' = Returns clean article text (Exa style).
            'code'    = Returns only headers, code blocks, and tables (Ref style).
            'auto'    = Detects if it's a doc site and switches to 'code' mode.

    Returns:
        Parsed and cleaned content from the URL.
    """
    logger.info(f"Read requested - URL: '{url}', Focus: {focus}")

    # Validate inputs
    if not url or not url.strip():
        error_msg = "URL cannot be empty"
        logger.error(error_msg)
        return f"Error: {error_msg}"

    if focus not in ["auto", "general", "code"]:
        error_msg = f"Invalid focus '{focus}'. Must be 'auto', 'general', or 'code'"
        logger.error(error_msg)
        return f"Error: {error_msg}"

    url = url.strip()

    # Validate URL format
    if not url.startswith(("http://", "https://")):
        error_msg = "URL must start with http:// or https://"
        logger.error(error_msg)
        return f"Error: {error_msg}"

    # Auto-detection logic
    original_focus = focus
    if focus == "auto":
        technical_indicators = ["docs", "api", "reference", "github", "guide", "documentation"]
        if any(ind in url.lower() for ind in technical_indicators):
            focus = "code"
            logger.debug(f"Auto-detected technical site, switching to code focus")
        else:
            focus = "general"
            logger.debug(f"Auto-detected general site, using general focus")

    async with httpx.AsyncClient(
        follow_redirects=True,
        headers={"User-Agent": "NexusMCP/1.0"},
        timeout=REQUEST_TIMEOUT
    ) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()

            logger.debug(f"Successfully fetched URL: {url} (Status: {response.status_code})")

            soup = bs4.BeautifulSoup(response.text, 'html.parser')

            # Pre-cleaning (Remove junk common to all modes)
            for trash in soup(["script", "style", "nav", "footer", "iframe", "svg", "noscript"]):
                trash.decompose()

            output = []
            output.append(f"=== SOURCE: {url} ===")
            output.append(f"=== MODE: {focus.upper()} ===\n")

            if focus == "code":
                # REF MODE (High Signal / Low Noise)
                relevant_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'pre', 'code', 'table'])

                for tag in relevant_tags:
                    if tag.name in ['h1', 'h2', 'h3', 'h4']:
                        header_text = tag.get_text(strip=True)
                        if header_text:
                            output.append(f"\n## {header_text}")
                    elif tag.name == 'pre':
                        code_text = tag.get_text()
                        if code_text.strip():
                            output.append(f"```\n{code_text}\n```")
                    elif tag.name == 'code' and tag.parent.name != 'pre':
                        code_text = tag.get_text(strip=True)
                        if code_text:
                            output.append(f"`{code_text}`")
                    elif tag.name == 'table':
                        # Enhanced table extraction
                        try:
                            rows = tag.find_all('tr')
                            if rows:
                                output.append("\n[Table]")
                                for row in rows[:10]:  # Limit to first 10 rows
                                    cells = row.find_all(['td', 'th'])
                                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                                    if cell_texts:
                                        output.append(" | ".join(cell_texts))
                        except Exception as table_error:
                            logger.warning(f"Table parsing failed: {table_error}")
                            output.append("\n[Table - parsing failed]")

                if len(output) < MIN_CODE_ELEMENTS_THRESHOLD:
                    fallback_msg = f"Code-focused extraction found minimal content ({len(output)} elements). The page may not contain structured documentation. Try focus='general' for better results."
                    logger.warning(f"Insufficient code elements found at {url}")
                    return fallback_msg

            else:
                # GENERAL MODE (Full Context)
                text = soup.get_text(separator='\n')
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                output.append("\n".join(lines))

            result = "\n".join(output)[:MAX_CONTENT_LENGTH]
            logger.info(f"Read successful - Extracted {len(result)} characters from {url}")

            if len("\n".join(output)) > MAX_CONTENT_LENGTH:
                result += f"\n\n[Content truncated at {MAX_CONTENT_LENGTH} characters]"
                logger.debug(f"Content truncated for {url}")

            return result

        except httpx.TimeoutException:
            error_msg = f"Request timed out after {REQUEST_TIMEOUT}s"
            logger.error(f"Timeout reading {url}")
            return f"Error: {error_msg}"
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.reason_phrase}"
            logger.error(f"HTTP error reading {url}: {error_msg}")
            return f"Error: {error_msg}"
        except httpx.RequestError as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"Network error reading {url}: {error_msg}")
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Unexpected error reading URL: {str(e)}"
            logger.exception(f"Unexpected error reading {url}")
            return f"Error: {error_msg}"

def main():
    """Entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
