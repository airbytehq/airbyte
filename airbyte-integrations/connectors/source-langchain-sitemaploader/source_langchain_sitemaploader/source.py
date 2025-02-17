"""
This connector uses LangChain’s SiteMapLoader to load pages from a sitemap.
It is modeled after the Airbyte “Reading a Page” example (e.g. the survey monkey demo)
found at:
https://docs.airbyte.com/connector-development/tutorials/custom-python-connector/reading-a-page
"""

from typing import Any, Iterable, List, Mapping, Optional, Tuple
import logging

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

# Import the SiteMapLoader from the LangChain Community package.
from langchain_community.document_loaders.sitemap import SitemapLoader

logger = logging.getLogger("airbyte")


class SitemapStream(Stream):
    """
    A stream that loads and yields records from a sitemap.

    Each record contains the page content (as "content") and associated metadata.
    """

    # No natural primary key for this source
    primary_key = ["url"]
    # Incremental sync configuration:
    # - Specify the cursor field that your API (or in this case, the document metadata) contains.
    # - Indicate that the source itself provides a cursor.
    # - Provide a default cursor field.
    cursor_field = ["lastmod"]
    source_defined_cursor = True
    default_cursor_field = ["lastmod"]

    def __init__(self, sitemap_url: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.sitemap_url = sitemap_url

    def read_records(
        self,
        sync_mode: str,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # Initialize the SiteMapLoader with the sitemap URL.
        loader = SitemapLoader(web_path=self.sitemap_url)
        # (Optional: adjust settings, e.g., loader.requests_per_second, loader.requests_kwargs)
        docs = loader.load()

        # Get the current state (if any). We assume state is a dict with "lastmod"
        state_cursor = stream_state.get("lastmod") if stream_state else None

        for doc in docs:
            record_cursor = doc.metadata.get("lastmod")
            url = doc.metadata.get("loc")
            changefreq = doc.metadata.get("changefreq")
            priority = doc.metadata.get("priority")
            # If no state exists or this record's cursor is more recent than the stored one, yield it.
            if state_cursor is None or record_cursor > state_cursor:
                yield {
                    "url": url,
                    "content": doc.page_content,
                    "lastmod": record_cursor,
                    "changefreq": changefreq,
                    "priority": priority,
                }

    def get_updated_state(
        self, current_stream_state: Mapping[str, Any], latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        # Retrieve the last known cursor value from state
        current_cursor = (
            current_stream_state.get("lastmod") if current_stream_state else None
        )
        latest_cursor = latest_record["lastmod"]
        # If no state exists, the latest record becomes the new state.
        if current_cursor is None:
            return {"lastmod": latest_cursor}
        # Otherwise, update the state with the maximum (i.e. most recent) value.
        new_cursor = max(current_cursor, latest_cursor)
        return {"lastmod": new_cursor}


class SourceLangchainSitemapLoader(AbstractSource):
    """
    The Airbyte source connector for loading documents using LangChain's SiteMapLoader.

    It implements check_connection() to validate that the sitemap returns at least one document,
    and streams() to expose the SitemapStream.
    """

    def check_connection(
        self, logger: logging.Logger, config: Mapping[str, Any]
    ) -> Tuple[bool, any]:
        # Fallback to module logger if logger is None.
        if logger is None:
            logger = logging.getLogger("airbyte")
        try:
            sitemap_url = config["sitemap_url"]
            loader = SitemapLoader(web_path=sitemap_url)
            docs = loader.load()
            if not docs:
                message = f"No documents found at sitemap {sitemap_url}"
                logger.error(message)
                return False, message
            return True, None
        except Exception as e:
            logger.exception("Error checking connection")
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        sitemap_url = config["sitemap_url"]
        return [SitemapStream(sitemap_url=sitemap_url)]
