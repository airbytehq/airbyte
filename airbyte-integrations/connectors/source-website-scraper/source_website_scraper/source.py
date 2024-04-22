import logging
import os
import fnmatch
import pytz
import uuid
import pandas as pd

from datetime import datetime
from abc import ABC
from twisted.internet import reactor
from multiprocessing import Process
from typing import Iterable, List, Mapping, Optional, Any, MutableMapping
from scrapy import signals
from scrapy.crawler import Crawler

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    SyncMode,
    Type,
    AirbyteLogMessage,
)
from airbyte_cdk.sources.streams import Stream
from .spiders.web_base import WebBaseSpider
from .spiders.sitemap import SitemapSpider


class Website(Stream, ABC):
    primary_key = "source"

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.data_dir = "storage/exports"
        self.url = config["url"]
        self.closespider_pagecount = config.get("closespider_pagecount", 100)
        self.allowed_extensions = config.get("allowed_types", ["html"])
        self.data_resource_id = str(uuid.uuid4())

    def run_spider(self):

        crawler = (
            Crawler(
                SitemapSpider,
                settings={
                    "CLOSESPIDER_PAGECOUNT": self.closespider_pagecount,
                },
            )
            if self.url.endswith("xml")
            else Crawler(
                WebBaseSpider,
                settings={
                    "CLOSESPIDER_PAGECOUNT": self.closespider_pagecount,
                },
            )
        )

        crawler.signals.connect(reactor.stop, signal=signals.spider_closed)  # type: ignore
        extra_args = {
            "url": self.url,
            "data_resource_id": self.data_resource_id,
            "allowed_extensions": self.allowed_extensions,
        }
        crawler.crawl(**extra_args)
        reactor.run()  # type: ignore

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[AirbyteRecordMessage]:
        process = Process(target=self.run_spider)
        process.start()
        process.join()
        pattern = f"{self.data_resource_id}*.csv"
        for filename in os.listdir(self.data_dir):
            if fnmatch.fnmatch(filename, pattern):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    df = pd.read_csv(file_path)
                    for _, row in df.iterrows():
                        transformed_row = {
                            "content": row.get("content"),
                            "data_resource_id": self.data_resource_id,
                            "source": row.get("source"),
                        }
                        record = AirbyteRecordMessage(
                            stream=self.name,  # Stream name
                            data=transformed_row,
                            emitted_at=int(datetime.now(tz=pytz.UTC).timestamp() * 1000),
                            meta={"file_path": file_path},
                        )
                        yield record
                except Exception as e:
                    raise e

    def get_json_schema(self):
        # Return the JSON schema for this stream
        return {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "source": {"type": "string"},
                "data_resource_id": {"type": "string"},
            },
        }


class SourceWebsiteScraper(AbstractSource):
    def check_connection(self, logger, config) -> str:
        # Check if the connection is valid
        return True, None

    def streams(self, config) -> Iterable[Stream]:
        # Return a list of streams
        return [Website(config)]

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterable[AirbyteMessage]:
        stream = Website(config)

        logger.info(f"Syncing stream: {stream.name}, {stream.config}")
        try:
            for record in stream.read_records(SyncMode.full_refresh):
                logger.info(f"Syncing Record: {record}")
                yield AirbyteMessage(type=Type.RECORD, record=record)
        except Exception as e:
            logger.error(f"Failed to read stream {stream.name}: {repr(e)}")
            yield AirbyteMessage(
                type=Type.LOG, log=AirbyteLogMessage(level="FATAL", message=f"Failed to read stream {stream.name}: {repr(e)}")
            )
