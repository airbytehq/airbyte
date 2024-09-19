#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from datetime import datetime

from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from source_gcs.helpers import GCSRemoteFile


class Cursor(DefaultFileBasedCursor):
    @staticmethod
    def get_file_uri(file: GCSRemoteFile) -> str:
        file_uri = file.displayed_uri if file.displayed_uri else file.uri
        return file_uri.split("?")[0]

    def add_file(self, file: GCSRemoteFile) -> None:
        uri = self.get_file_uri(file)
        self._file_to_datetime_history[uri] = file.last_modified.strftime(self.DATE_TIME_FORMAT)
        if len(self._file_to_datetime_history) > self.DEFAULT_MAX_HISTORY_SIZE:
            # Get the earliest file based on its last modified date and its uri
            oldest_file = self._compute_earliest_file_in_history()
            if oldest_file:
                del self._file_to_datetime_history[oldest_file.uri]
            else:
                raise Exception(
                    "The history is full but there is no files in the history. This should never happen and might be indicative of a bug in the CDK."
                )

    def _should_sync_file(self, file: GCSRemoteFile, logger: logging.Logger) -> bool:
        uri = self.get_file_uri(file)
        if uri in self._file_to_datetime_history:
            # If the file's uri is in the history, we should sync the file if it has been modified since it was synced
            updated_at_from_history = datetime.strptime(self._file_to_datetime_history[uri], self.DATE_TIME_FORMAT)
            if file.last_modified < updated_at_from_history:
                logger.warning(
                    f"The file {uri}'s last modified date is older than the last time it was synced. This is unexpected. Skipping the file."
                )
            else:
                return file.last_modified > updated_at_from_history
            return file.last_modified > updated_at_from_history
        if self._is_history_full():
            if self._initial_earliest_file_in_history is None:
                return True
            if file.last_modified > self._initial_earliest_file_in_history.last_modified:
                # If the history is partial and the file's datetime is strictly greater than the earliest file in the history,
                # we should sync it
                return True
            elif file.last_modified == self._initial_earliest_file_in_history.last_modified:
                # If the history is partial and the file's datetime is equal to the earliest file in the history,
                # we should sync it if its uri is strictly greater than the earliest file in the history
                return uri > self._initial_earliest_file_in_history.uri
            else:
                # Otherwise, only sync the file if it has been modified since the start of the time window
                return file.last_modified >= self.get_start_time()
        else:
            # The file is not in the history and the history is complete. We know we need to sync the file
            return True
