#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from typing import Iterator

import pendulum
from airbyte_cdk.sources.streams.files import FileInfo, IncrementalFilesStream
from google.cloud import storage
from source_google_cloud_storage.google_cloud_storage_file import GoogleCloudStorageFile


class GoogleCloudStorageStream(IncrementalFilesStream):
    @property
    def storagefile_class(self) -> type:
        return GoogleCloudStorageFile

    def file_iterator(self) -> Iterator[FileInfo]:
        """
        TODO: Code the functionality to connect to the container/bucket and yield a FileInfo instance for every file inside
            - you can access the fields you specify in spec.py in the dict `self._provider`, such as credentials.
            - ideally you can do a 'list'-like function on the container which will return all the files with their properties.
            - you don't need to do any filtering on patterns or timestamps here, that is all handled by the parent class.
            - To build the FileInfo instances, you'll need:
                - a key for each file which should be unique. This would typically be the url / filepath.
                - the last modified timestamp on the file. You'll need to work out how to obtain this property from the provider.
                - the size of the file in bytes. If this can't be obtained, just use a value of 1, it isn't functionally required.

        :yield: FileInfo instance
        """
        if self._provider.get("service_account_json"):
            service_account_json = json.loads(self._provider.get("service_account_json"), strict=False)
            client = storage.Client.from_service_account_info(service_account_json)
            blob_iter = client.list_blobs(self._provider.get("bucket"))
        else:
            client = storage.Client.create_anonymous_client()
            blob_iter = client.bucket(self._provider.get("bucket"), user_project=None).list_blobs()

        # pagination is automatically handled by gcs library so this lists all blobs
        for blob in blob_iter:
            if not blob.name.endswith("/"):  # filter out 'directories'
                yield FileInfo(blob.name, blob._properties.get("size"), pendulum.parse(blob._properties.get("updated")))
