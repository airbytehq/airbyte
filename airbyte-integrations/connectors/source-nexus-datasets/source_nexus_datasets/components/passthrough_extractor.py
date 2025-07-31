import logging
from typing import Any, Iterable, Mapping

from airbyte_cdk.sources.declarative.extractors.extractor import Extractor

logger = logging.getLogger("airbyte")

class PassthroughExtractor(Extractor):
    """
    A simple extractor that yields the input data directly as records.
    This is useful when the decoder already produces well-formed dictionaries
    that should be treated as individual records.
    """
    def __init__(self, config: Mapping[str, Any], **kwargs):
        """
        Initializes the PassthroughExtractor.

        Args:
            config (Mapping[str, Any]): The connector configuration.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(config=config, **kwargs)

    def extract_records(
        self,
        response: Any, # This will be the dictionary yielded by your FlexibleDecoder
        field_path: list[str] | None = None, # Not used for passthrough
        config: Mapping[str, Any] | None = None # Not used for passthrough
    ) -> Iterable[Mapping[str, Any]]:
        """
        Yields the input 'response' directly as a record.
        Assumes 'response' is already a single dictionary representing a record.
        """
        if isinstance(response, Mapping):
            # If the decoder yielded a single dictionary, yield it directly
            yield response
        elif isinstance(response, Iterable):
            # If the decoder somehow yielded an iterable of dictionaries, yield from it
            for item in response:
                if isinstance(item, Mapping):
                    yield item
                else:
                    logger.warning(f"PassthroughExtractor found non-mapping item in iterable: {type(item)}. Skipping.")
        else:
            logger.error(f"PassthroughExtractor received unexpected input type: {type(response)}. Expected Mapping or Iterable[Mapping].")
            raise ValueError(f"PassthroughExtractor expected a mapping or iterable of mappings, got: {type(response)}")
