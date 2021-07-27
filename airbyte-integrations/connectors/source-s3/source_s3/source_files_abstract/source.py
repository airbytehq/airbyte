#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from abc import ABC, abstractmethod
from fnmatch import fnmatch
from traceback import format_exc
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream


class SourceFilesAbstract(AbstractSource, ABC):
    @property
    @abstractmethod
    def stream_class(self) -> type:
        """
        :return: reference to the relevant FileStream class e.g. IncrementalFileStreamS3
        """

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        This method checks two things:
            - That the credentials provided in config are valid for access.
            - That the path pattern(s) provided in config are valid to be matched against.

        :param logger: an instance of AirbyteLogger to use
        :param config: The user-provided configuration as specified by the source's spec. This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful and we can connect to the underlying data
        source using the provided configuration.
        Otherwise, the input config cannot be used to connect to the underlying data source, and the "error" object should describe what went wrong.
        The error object will be cast to string to display the problem to the user.
        """

        found_a_file = False
        try:
            for filepath in self.stream_class.filepath_iterator(logger, config.get("provider")):
                found_a_file = True
                for path_pattern in config.get("path_patterns"):
                    fnmatch(filepath, path_pattern)  # test that matching on the pattern doesn't error
                break  # just need first file here to test connection and valid patterns

        except Exception as e:
            logger.error(format_exc())
            return (False, e)

        else:
            if not found_a_file:
                logger.warn("Found 0 files (but connection is valid).")
            return (True, None)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        We just have a single stream per source so construct that here

        :param config: The user-provided configuration as specified by the source's spec.
        :return: A list of the streams in this source connector.
        """
        return [self.stream_class(**config)]
