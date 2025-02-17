import pytest
from source_langchain_sitemaploader.source import (
    SourceLangchainSitemapLoader,
    SitemapStream,
)

# --- Helpers for testing ---


class FakeDoc:
    """
    A fake document class that mimics the objects returned by SiteMapLoader.load().
    """

    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata


def fake_load_success(self):
    """
    Fake load method returning two fake documents.
    """
    return [
        FakeDoc("Fake content 1", {"loc": "https://example.com/page1"}),
        FakeDoc("Fake content 2", {"loc": "https://example.com/page2"}),
    ]


def fake_load_empty(self):
    """
    Fake load method returning an empty list to simulate no documents found.
    """
    return []


# --- Pytest fixture ---


@pytest.fixture
def valid_config():
    """
    Returns a sample configuration with a sitemap_url.
    """
    return {"sitemap_url": "https://example.com/sitemap.xml"}


# --- Integration Tests ---


def test_integration_check_connection_success(monkeypatch, valid_config):
    """
    Test that check_connection succeeds when the sitemap loader returns documents.
    """
    from langchain_community.document_loaders.sitemap import SitemapLoader

    monkeypatch.setattr(SitemapLoader, "load", fake_load_success)

    source = SourceLangchainSitemapLoader()
    success, error = source.check_connection(logger=None, config=valid_config)
    assert success is True
    assert error is None


def test_integration_check_connection_failure(monkeypatch, valid_config):
    """
    Test that check_connection fails when the sitemap loader returns no documents.
    """
    from langchain_community.document_loaders.sitemap import SitemapLoader

    monkeypatch.setattr(SitemapLoader, "load", fake_load_empty)

    source = SourceLangchainSitemapLoader()
    success, error = source.check_connection(logger=None, config=valid_config)
    assert success is False
    assert "No documents found" in error


def test_integration_read_records(monkeypatch, valid_config):
    """
    Test that the stream's read_records yields the expected records.
    """
    from langchain_community.document_loaders.sitemap import SitemapLoader

    monkeypatch.setattr(SitemapLoader, "load", fake_load_success)

    stream = SitemapStream(sitemap_url=valid_config["sitemap_url"])
    records = list(stream.read_records(sync_mode="full_refresh"))

    # Verify that two records were yielded with expected content and metadata.
    assert len(records) == 2
    assert records[0]["content"] == "Fake content 1"
    assert records[0]["url"] == "https://example.com/page1"
    assert records[1]["content"] == "Fake content 2"
    assert records[1]["url"] == "https://example.com/page2"
