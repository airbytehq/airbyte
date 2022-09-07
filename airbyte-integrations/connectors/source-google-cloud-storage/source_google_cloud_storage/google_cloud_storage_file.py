#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from contextlib import contextmanager
from typing import BinaryIO, Iterator, TextIO, Union

from airbyte_cdk.sources.streams.files import StorageFile
from google.cloud import storage
from smart_open import open as smart_open


class GoogleCloudStorageFile(StorageFile):
    @contextmanager
    def open(self, binary: bool) -> Iterator[Union[TextIO, BinaryIO]]:
        """
        :param binary: whether or not to open file as binary
        :return: file-like object
        """
        # TODO: Code functionality to open a specific file from the provider container/bucket
        #    - you can access the fields you specify in spec.py in the dict `self._provider`, such as credentials.
        #    - you can access the specific file's FileInfo object using `self.file_info`.
        #    - Recommendation: utilise smart_open (https://github.com/RaRe-Technologies/smart_open) if it supports your source.
        #    - e.g. result = smart_open.open(f"s3://{bucket}/{self.url}", transport_params=params, mode=mode)
        if self._provider.get("service_account_json"):
            service_account_json = json.loads(self._provider.get("service_account_json"), strict=False)
            client = storage.Client.from_service_account_info(service_account_json)
        else:
            client = storage.Client.create_anonymous_client()

        mode = "rb" if binary else "r"
        bucket = self._provider.get("bucket")
        result = smart_open(f"gs://{bucket}/{self.url}", transport_params=dict(client=client), mode=mode)

        try:
            yield result
        finally:
            result.close()
