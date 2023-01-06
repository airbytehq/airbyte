#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from traceback import format_exc
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from wcmatch.glob import GLOBSTAR, SPLIT, globmatch

# ideas on extending this to handle multiple streams:
# - "dataset" is currently the name of the single table/stream. We could allow comma-split table names in this string for many streams.
# - "path_pattern" currently uses https://facelessuser.github.io/wcmatch/glob/ to match a single string pattern (can be multiple | separated)
#   we could change this to a JSON string in format {"stream_name": "pattern(s)"} to allow many streams and match to names in dataset.
# - "format" I think we'd have to enforce like-for-like formats across streams otherwise the UI would become chaotic imo.
# - "schema" could become a nested object such as {"stream_name": {schema}} allowing specifying schema for one/all/none/some tables.


class SourceFilesAbstract(AbstractSource, ABC):
    @property
    @abstractmethod
    def stream_class(self) -> type:
        """
        :return: reference to the relevant FileStream class e.g. IncrementalFileStreamS3
        """

    @property
    @abstractmethod
    def spec_class(self) -> type:
        """
        :return: reference to the relevant pydantic spec class e.g. SourceS3Spec
        """

    @property
    @abstractmethod
    def documentation_url(self) -> str:
        """
        :return: link to docs page for this source e.g. "https://docs.airbyte.com/integrations/sources/s3"
        """

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        This method checks two things:
            - That the credentials provided in config are valid for access.
            - That the path pattern(s) provided in config are valid to be matched against.

        :param logger: an instance of AirbyteLogger to use
        :param config: The user-provided configuration as specified by the source's spec.
                                This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful and we can connect to the underlying data
        source using the provided configuration.
        Otherwise, the input config cannot be used to connect to the underlying data source, and the "error" object should describe what went wrong.
        The error object will be cast to string to display the problem to the user.
        """
        try:
            stream = self.stream_class(**config)
            stream.fileformatparser_class(stream._format)._validate_config(config)
            for file_info in stream.filepath_iterator():
                # TODO: will need to split config.get("path_pattern") up by stream once supporting multiple streams
                # test that matching on the pattern doesn't error
                globmatch(file_info.key, config.get("path_pattern"), flags=GLOBSTAR | SPLIT)
                # just need first file here to test connection and valid patterns
                return True, None

        except Exception as e:
            logger.error(format_exc())
            return False, e

        logger.warn("Found 0 files (but connection is valid).")
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        We just have a single stream per source so construct that here

        :param config: The user-provided configuration as specified by the source's spec.
        :return: A list of the streams in this source connector.
        """
        return [self.stream_class(**config)]

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        # make dummy instance of stream_class in order to get 'supports_incremental' property
        incremental = self.stream_class(dataset="", provider="", format="", path_pattern="").supports_incremental

        supported_dest_sync_modes = [DestinationSyncMode.overwrite]
        if incremental:
            supported_dest_sync_modes.extend([DestinationSyncMode.append, DestinationSyncMode.append_dedup])

        return ConnectorSpecification(
            documentationUrl=self.documentation_url,
            changelogUrl=self.documentation_url,
            supportsIncremental=incremental,
            supported_destination_sync_modes=supported_dest_sync_modes,
            connectionSpecification=self.spec_class.schema(),  # type: ignore[attr-defined]
        )
