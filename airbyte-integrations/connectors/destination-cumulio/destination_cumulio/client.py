#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import time
from logging import Logger
from typing import Any, Mapping

from cumulio.cumulio import Cumulio  # type: ignore


# def _retry_with_backoff(
#     fn: Callable,
#     backoff_times_in_seconds: list[int]
# ):
#     while True:
#         try:
#             return fn()


class CumulioClient:
    # Cumul.io will auto-generate a UUID that is unique to the dataset created.
    # To ensure a consistent flow to the same dataset, we'll add a tag to the dataset:
    # the tag is a combination of the prefix below and the stream name.
    # This allows us to retrieve the same dataset resource upon further sync schedules.
    TAG_PREFIX = "[AIRBYTE - DO NOT DELETE] - "

    REPLACE_TAG = "REPLACE DATA"

    INITIAL_DATASET_NAME_PREFIX = "Airbyte - "

    BACKOFF_TIMES_IN_SECONDS = [300, 600, 1200]

    def __init__(self, config: Mapping[str, Any], logger: Logger):
        self.logger = logger
        self.client = Cumulio(config["api_key"], config["api_token"], config["api_host"])

    def batch_write(
        self,
        stream_name: str,
        write_buffer: list,
        column_headers: list,
        is_in_overwrite_sync_mode: bool,
        is_first_batch: bool,
        update_metadata: bool,
    ):
        """Write a list of data (array of arrays) in a specific sync mode to Cumul.io."""
        if len(write_buffer) == 0 or (len(write_buffer) == 1 and len(write_buffer[0]) == 0):
            return

        dataset_id = self._get_dataset_id_from_stream_name(stream_name)
        if dataset_id is None:
            dataset_id = self._push_batch_to_new_dataset(stream_name, write_buffer, column_headers)
        else:
            is_in_replace_mode = self._dataset_contains_replace_tag(dataset_id)
            first_batch_replace = is_first_batch and (is_in_overwrite_sync_mode or is_in_replace_mode)
            self._push_batch_to_existing_dataset(
                dataset_id,
                write_buffer,
                column_headers,
                first_batch_replace,
                update_metadata,
            )

        self.logger.info(f"Successfully pushed {len(write_buffer)} rows to Cumul.io's data warehouse in a dataset with id {dataset_id}.")

    def test_api_token(self):
        """Test an API key and token by retrieving it."""
        self.logger.info("Checking API host, key and token.")
        data = self.client.get("authorization", {"where": {"type": "api"}})
        # if response contains a count 0, the API host, key and token combination is unknown to Cumul.io.
        if data["count"] == 0:
            raise Exception(
                "Unknown combination of API host, key and token. Can you verify whether you've specified the correct combination of "
                "Cumul.io API host, key, and token?"
            )
        self.logger.info("API host, key and token combination is valid.")

    def test_data_push(self, stream_name: str, data: list[list[Any]], columns: list[str]):
        """[DEPRECATED] This method is no longer in use as it results in a lot of overhead.
        Test pushing dummy data into a dataset, and delete the dataset afterwards."""

        self.logger.info("Starting data push of dummy data.")
        self.batch_write(stream_name, data, columns, True, True, True)
        self.logger.info("Finished data push of dummy data. Will delete dummy dataset.")

        self.delete_dataset(stream_name)
        self.logger.info("Finished deleting dummy dataset.")

    def delete_dataset(self, stream_name: str):
        """Delete a dataset in Cumul.io.
        This should only be used for testing purposes. Currently used in:
          - Integration tests
          - When pushing dummy data to an example dataset during "check" of Airbyte destination connector (see destination.py check method)
        """
        dataset_id = self._get_dataset_id_from_stream_name(stream_name)
        if dataset_id is not None:
            return self.client.delete("securable", dataset_id)

        self.logger.info(f"No dataset for stream {stream_name} found to delete.")

    def get_ordered_columns(self, stream_name: str):
        """Return a list of ordered columns (based on their order in Cumul.io).
        The dataset is retrieved based on a Cumul.io tag that includes the stream_name.
        """
        dataset_and_columns = self.get_dataset_and_columns_from_stream_name(stream_name)
        if dataset_and_columns is None:
            # Dataset hasn't been created yet on Cumul.io's side.
            return []
        # Sort columns based on the order property.
        order_sorted_columns = sorted(dataset_and_columns["columns"], key=lambda x: x["order"])
        # Return a list of column source names.
        return [column["source_name"] for column in order_sorted_columns]

    def get_dataset_and_columns_from_stream_name(self, stream_name: str):
        """Return a dataset and its columns based on a Cumul.io tag that includes the stream_name."""
        result = self.client.get(
            "securable",
            {
                "where": {"type": "dataset"},
                "attributes": ["id", "name"],
                "include": [
                    {
                        "model": "Tag",
                        "where": {"tag": self.TAG_PREFIX + stream_name},
                        "attributes": ["id", "tag"],
                        "jointype": "inner",
                    },
                    {
                        "model": "Column",
                        "attributes": ["id", "source_name", "order"],
                        "jointype": "inner",
                    },
                ],
            },
        )
        if result["count"] > 1:
            raise Exception(
                f"More than one dataset has been returned, could you verify whether the tag for stream {stream_name} is set up "
                f"correctly in Cumul.io (expected a tag '{self.TAG_PREFIX}{stream_name}')?"
            )
        # A count of zero means that the dataset has not been created on Cumul.io's side yet.
        # We'll return None to indicate this.
        elif result["count"] == 0:
            return None
        # return dataset and its columns.
        return result["rows"][0]

    def set_replace_tag_on_dataset(self, stream_name: str):
        """Add a "replace" tag to a specific dataset based on the stream_name.
        The "replace" tag is used to ensure that the next sync will replace the existing data.
        """
        dataset_id = self._get_dataset_id_from_stream_name(stream_name)
        if dataset_id is not None:
            self.logger.info(
                f"A tag will be added to the dataset with id {dataset_id} to replace the existing data upon next sync. "
                f"As a result, the existing data will not be replaced until the next sync has ran. "
                f"This avoids empty datasets which cause 'No data' to be displayed upon querying them."
            )
            return self._associate_tag_dataset_id(self.REPLACE_TAG, dataset_id)
        self.logger.debug(
            f"No dataset found to set Replace tag on (looking for stream name '{stream_name}'), "
            f"this might be due to the dataset not existing yet on Cumul.io's side."
        )

    def _push_batch_to_new_dataset(self, stream_name: str, write_buffer: list[list[Any]], column_headers: list[str]):
        properties = {
            "type": "create",
            "data": write_buffer,
            "options": {
                "header": column_headers,
                "update_metadata": True,
                "name": {"en": self.INITIAL_DATASET_NAME_PREFIX + stream_name},
            },
        }
        result: Mapping[str, Any] = {}
        data_is_pushed = False
        try_count = 0
        while (not data_is_pushed) and try_count < len(self.BACKOFF_TIMES_IN_SECONDS):
            try:
                self.logger.info(
                    f"Pushing {len(write_buffer)} rows to Cumul.io's data warehouse in a new Cumul.io dataset "
                    f"with name {self.INITIAL_DATASET_NAME_PREFIX}{stream_name}."
                )

                result = self.client.create("data", properties)
                data_is_pushed = True

            except Exception as e:
                if "Unauthorized" in str(e):
                    raise Exception(
                        f"Not able to push a batch of data to a new dataset due to an 'Unauthorized' error. "
                        f"Please verify that your API key and token are still valid!"
                        f"Error: {e}"
                    )
                elif try_count + 1 >= len(self.BACKOFF_TIMES_IN_SECONDS):
                    raise Exception(f"Exception while creating new dataset after {len(self.BACKOFF_TIMES_IN_SECONDS)} retries: {e}")

                seconds_to_backoff = self.BACKOFF_TIMES_IN_SECONDS[try_count]
                try_count += 1
                self.logger.info(
                    f"Error pushing data to a new dataset during try {try_count}, retrying in {seconds_to_backoff} seconds. Error: {e}"
                )
                time.sleep(seconds_to_backoff)

        dataset_id = result["rows"][0]["id"]
        try:
            # Add a tag to the dataset to allow retrieving it upon further syncs / batch writes
            self._associate_tag_dataset_id(stream_name, dataset_id)
        except Exception as e:
            raise Exception(
                f"The data has been stored successfully, but an error occurred while associating a required tag to the "
                f"dataset (id: {dataset_id}). This will likely cause issues upon further synchronizations. The following "
                f"error occurred: ",
                e,
            )

        return dataset_id

    def _push_batch_to_existing_dataset(
        self,
        dataset_id: str,
        write_buffer: list[list[Any]],
        column_headers: list[str],
        first_batch_replace: bool,
        update_metadata: bool,
    ):
        cumulio_sync_type = "replace" if first_batch_replace else "append"

        properties = {
            "type": cumulio_sync_type,
            "data": write_buffer,
            "securable_id": dataset_id,
            "options": {
                "header": column_headers,
                "update_metadata": update_metadata,
            },
        }
        data_is_pushed = False
        try_count = 0
        while (not data_is_pushed) and try_count < len(self.BACKOFF_TIMES_IN_SECONDS):
            try:
                self.logger.info(
                    f"Pushing {len(write_buffer)} rows to Cumul.io dataset with id {dataset_id} in {cumulio_sync_type} mode, "
                    f"{'while' if update_metadata else 'not'} updating the columns of that dataset."
                )
                self.client.create("data", properties)

                data_is_pushed = True

                if first_batch_replace:
                    # Try to remove replace tag to ensure next syncs do not replace existing data.
                    self._remove_replace_tag_dataset_id_association(dataset_id)

            except RuntimeError as e:
                if "Unauthorized" in str(e):
                    raise Exception(
                        f"Not able to push a batch of data to dataset {dataset_id} due to an 'Unauthorized' error. "
                        f"Please verify that your API key and token are still valid!"
                        f"Error: {e}"
                    )
                elif try_count + 1 >= len(self.BACKOFF_TIMES_IN_SECONDS):
                    raise Exception(
                        f"Exception while pushing to existing dataset {dataset_id} after {len(self.BACKOFF_TIMES_IN_SECONDS)} retries: ",
                        e,
                    )

                seconds_to_backoff = self.BACKOFF_TIMES_IN_SECONDS[try_count]
                try_count += 1

                self.logger.info(
                    f"Error pushing data to existing dataset {dataset_id} during try {try_count}, retrying in {seconds_to_backoff} seconds."
                )

                time.sleep(seconds_to_backoff)

    def _dataset_contains_replace_tag(self, dataset_id: str):
        """Return a boolean to indicate whether a dataset contains the "replace" tag."""
        result = self.client.get(
            "securable",
            {
                "where": {"type": "dataset", "id": dataset_id},
                "attributes": ["id", "name"],
                "include": [
                    {
                        "model": "Tag",
                        "where": {"tag": self.TAG_PREFIX + self.REPLACE_TAG},
                        "attributes": ["id", "tag"],
                        "jointype": "inner",
                    }
                ],
            },
        )
        return False if result["count"] == 0 else True

    def _remove_replace_tag_dataset_id_association(self, dataset_id: str):
        """Remove the "replace" tag from a specific dataset."""
        tag_id = self._get_tag_id(self.REPLACE_TAG)
        if tag_id is not None:
            return self._dissociate_tag_with_dataset_id(tag_id, dataset_id)
        self.logger.debug(
            f"No replace tag found, so could not remove for Cumul.io dataset with id {dataset_id}."
            f"This could be expected as the stream might be configured in overwrite mode."
        )

    def _get_dataset_id_from_stream_name(self, stream_name: str):
        """Return a dataset ID based on a Cumul.io tag that includes the stream_name."""
        result = self.client.get(
            "securable",
            {
                "where": {"type": "dataset"},
                "attributes": ["id", "name"],
                "include": [
                    {
                        "model": "Tag",
                        "where": {"tag": self.TAG_PREFIX + stream_name},
                        "attributes": ["id", "tag"],
                        "jointype": "inner",
                    }
                ],
            },
        )
        if result["count"] > 1:
            raise Exception(
                f"More than one dataset has been found, could you verify whether the tag for stream {stream_name} is set up "
                f"correctly in Cumul.io (expected a tag '{self.TAG_PREFIX}{stream_name}' on a single dataset)?"
            )
        # A count of zero means that the dataset has not been created on Cumul.io's side yet.
        # We'll return None to indicate this.
        elif result["count"] == 0:
            return None
        # return dataset ID
        return result["rows"][0]["id"]

    def _associate_tag_dataset_id(self, tag_name: str, dataset_id: str):
        """Ensure that a specific stream name tag is associated to a dataset ID.
        Optionally the Tag is created and associated if not existing yet.
        """
        # A tag should be unique and cannot be created multiple times.
        # In order to ensure that the association doesn't fail,
        # we'll first try to retrieve the tag and then either
        # associate it with the newly created securable,
        # or create & associate it.
        tag_id = self._get_tag_id(tag_name)
        if tag_id is not None:
            return self._associate_tag_with_dataset_id(tag_id, dataset_id)
        return self._create_and_associate_stream_name_tag_with_dataset_id(tag_name, dataset_id)

    def _get_tag_id(self, tag_name: str):
        """Return a Tag ID using the stream name."""
        result = self.client.get("tag", {"where": {"tag": self.TAG_PREFIX + tag_name}})
        if result["count"] == 0:
            return None
        return result["rows"][0]["id"]

    def _associate_tag_with_dataset_id(self, tag_id: str, dataset_id: str):
        return self.client.associate("tag", tag_id, "Securables", dataset_id)

    def _dissociate_tag_with_dataset_id(self, tag_id: str, dataset_id: str):
        return self.client.dissociate("tag", tag_id, "Securables", dataset_id)

    def _create_and_associate_stream_name_tag_with_dataset_id(self, tag_name: str, dataset_id: str):
        return self.client.create(
            "tag",
            {"tag": self.TAG_PREFIX + tag_name},
            [{"role": "Securables", "id": dataset_id}],
        )
