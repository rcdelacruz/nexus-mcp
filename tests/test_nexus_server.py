import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx
from nexus_server import nexus_search, nexus_read


class TestNexusSearch:
    """Tests for the nexus_search tool."""

    @pytest.mark.asyncio
    async def test_search_success_general_mode(self):
        """Test successful search in general mode."""
        mock_results = [
            {
                'title': 'Test Result 1',
                'href': 'https://example.com/1',
                'body': 'This is a test snippet 1'
            },
            {
                'title': 'Test Result 2',
                'href': 'https://example.com/2',
                'body': 'This is a test snippet 2'
            }
        ]

        with patch('nexus_server.DDGS') as mock_ddgs:
            mock_instance = Mock()
            mock_instance.__enter__ = Mock(return_value=mock_instance)
            mock_instance.__exit__ = Mock(return_value=None)
            mock_instance.text = Mock(return_value=mock_results)
            mock_ddgs.return_value = mock_instance

            result = await nexus_search(query="test query", mode="general", max_results=2)

            assert "Test Result 1" in result
            assert "https://example.com/1" in result
            assert "This is a test snippet 1" in result
            assert "Test Result 2" in result

    @pytest.mark.asyncio
    async def test_search_success_docs_mode(self):
        """Test successful search in docs mode."""
        mock_results = [
            {
                'title': 'Python Docs',
                'href': 'https://docs.python.org',
                'body': 'Documentation for Python'
            }
        ]

        with patch('nexus_server.DDGS') as mock_ddgs:
            mock_instance = Mock()
            mock_instance.__enter__ = Mock(return_value=mock_instance)
            mock_instance.__exit__ = Mock(return_value=None)
            mock_instance.text = Mock(return_value=mock_results)
            mock_ddgs.return_value = mock_instance

            result = await nexus_search(query="python asyncio", mode="docs", max_results=1)

            assert "Python Docs" in result
            mock_instance.text.assert_called_once()
            call_args = mock_instance.text.call_args[0][0]
            assert "site:readthedocs.io" in call_args or "documentation" in call_args

    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        """Test search with empty query."""
        result = await nexus_search(query="", mode="general")
        assert "Error" in result
        assert "empty" in result.lower()

    @pytest.mark.asyncio
    async def test_search_invalid_mode(self):
        """Test search with invalid mode."""
        result = await nexus_search(query="test", mode="invalid_mode")
        assert "Error" in result
        assert "Invalid mode" in result

    @pytest.mark.asyncio
    async def test_search_no_results(self):
        """Test search that returns no results."""
        with patch('nexus_server.DDGS') as mock_ddgs:
            mock_instance = Mock()
            mock_instance.__enter__ = Mock(return_value=mock_instance)
            mock_instance.__exit__ = Mock(return_value=None)
            mock_instance.text = Mock(return_value=[])
            mock_ddgs.return_value = mock_instance

            result = await nexus_search(query="test", mode="general")

            assert "No results found" in result

    @pytest.mark.asyncio
    async def test_search_max_results_clamping(self):
        """Test that max_results is clamped to valid range."""
        mock_results = [{'title': 'Test', 'href': 'http://test.com', 'body': 'Test'}]

        with patch('nexus_server.DDGS') as mock_ddgs:
            mock_instance = Mock()
            mock_instance.__enter__ = Mock(return_value=mock_instance)
            mock_instance.__exit__ = Mock(return_value=None)
            mock_instance.text = Mock(return_value=mock_results)
            mock_ddgs.return_value = mock_instance

            # Test upper bound
            await nexus_search(query="test", max_results=100)
            assert mock_instance.text.call_args[1]['max_results'] == 20

            # Test lower bound
            await nexus_search(query="test", max_results=-5)
            assert mock_instance.text.call_args[1]['max_results'] == 1

    @pytest.mark.asyncio
    async def test_search_exception_handling(self):
        """Test search handles exceptions gracefully."""
        with patch('nexus_server.DDGS') as mock_ddgs:
            mock_ddgs.side_effect = Exception("Network error")

            result = await nexus_search(query="test", mode="general")

            assert "Error" in result
            assert "failed" in result.lower()


class TestNexusRead:
    """Tests for the nexus_read tool."""

    @pytest.mark.asyncio
    async def test_read_success_general_mode(self):
        """Test successful URL read in general mode."""
        mock_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <p>This is a test paragraph.</p>
                <p>Another paragraph with content.</p>
            </body>
        </html>
        """

        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock()
            mock_client.return_value = mock_client_instance

            result = await nexus_read(url="https://example.com", focus="general")

            assert "https://example.com" in result
            assert "GENERAL" in result
            assert "test paragraph" in result.lower()

    @pytest.mark.asyncio
    async def test_read_success_code_mode(self):
        """Test successful URL read in code mode."""
        mock_html = """
        <html>
            <body>
                <h1>Documentation</h1>
                <h2>Function Reference</h2>
                <pre>def example():
    return True</pre>
                <code>example_var</code>
            </body>
        </html>
        """

        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock()
            mock_client.return_value = mock_client_instance

            result = await nexus_read(url="https://docs.example.com", focus="code")

            assert "https://docs.example.com" in result
            assert "CODE" in result
            assert "Documentation" in result
            assert "def example" in result

    @pytest.mark.asyncio
    async def test_read_auto_detection_technical(self):
        """Test auto-detection switches to code mode for technical URLs."""
        mock_html = """
        <html><body>
            <h1>API Reference</h1>
            <h2>Overview</h2>
            <h3>Functions</h3>
            <pre>def example():
    return True</pre>
            <code>example_var</code>
        </body></html>
        """

        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock()
            mock_client.return_value = mock_client_instance

            result = await nexus_read(url="https://docs.python.org/api", focus="auto")

            assert "CODE" in result

    @pytest.mark.asyncio
    async def test_read_auto_detection_general(self):
        """Test auto-detection uses general mode for non-technical URLs."""
        mock_html = "<html><body><p>News article content</p></body></html>"

        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock()
            mock_client.return_value = mock_client_instance

            result = await nexus_read(url="https://news.example.com/article", focus="auto")

            assert "GENERAL" in result

    @pytest.mark.asyncio
    async def test_read_empty_url(self):
        """Test read with empty URL."""
        result = await nexus_read(url="", focus="general")
        assert "Error" in result
        assert "empty" in result.lower()

    @pytest.mark.asyncio
    async def test_read_invalid_url_format(self):
        """Test read with invalid URL format."""
        result = await nexus_read(url="not-a-valid-url", focus="general")
        assert "Error" in result
        assert "http" in result.lower()

    @pytest.mark.asyncio
    async def test_read_invalid_focus(self):
        """Test read with invalid focus parameter."""
        result = await nexus_read(url="https://example.com", focus="invalid")
        assert "Error" in result
        assert "Invalid focus" in result

    @pytest.mark.asyncio
    async def test_read_http_error(self):
        """Test read handles HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.get.return_value.raise_for_status = Mock(
                side_effect=httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
            )
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock()
            mock_client.return_value = mock_client_instance

            result = await nexus_read(url="https://example.com/notfound", focus="general")

            assert "Error" in result
            assert "404" in result

    @pytest.mark.asyncio
    async def test_read_timeout(self):
        """Test read handles timeout errors."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock()
            mock_client.return_value = mock_client_instance

            result = await nexus_read(url="https://example.com", focus="general")

            assert "Error" in result
            assert "timed out" in result.lower()

    @pytest.mark.asyncio
    async def test_read_network_error(self):
        """Test read handles network errors."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(
                side_effect=httpx.RequestError("Connection failed")
            )
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock()
            mock_client.return_value = mock_client_instance

            result = await nexus_read(url="https://example.com", focus="general")

            assert "Error" in result
            assert "Network error" in result

    @pytest.mark.asyncio
    async def test_read_content_truncation(self):
        """Test that large content is truncated."""
        long_content = "<html><body><p>" + ("A" * 10000) + "</p></body></html>"

        mock_response = Mock()
        mock_response.text = long_content
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock()
            mock_client.return_value = mock_client_instance

            result = await nexus_read(url="https://example.com", focus="general")

            assert len(result) <= 8100  # MAX_CONTENT_LENGTH + some buffer for headers

    @pytest.mark.asyncio
    async def test_read_code_mode_minimal_content(self):
        """Test code mode with minimal structured content."""
        mock_html = "<html><body><p>Just a paragraph, no code</p></body></html>"

        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock()
            mock_client.return_value = mock_client_instance

            result = await nexus_read(url="https://example.com", focus="code")

            assert "minimal content" in result.lower() or "focus='general'" in result
