#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.abstract_files_source import AbstractFilesSource
from source_google_cloud_storage.spec import SourceGoogleCloudStorageSpec
from source_google_cloud_storage.stream import GoogleCloudStorageStream


class SourceGoogleCloudStorage(AbstractFilesSource):
    stream_class = GoogleCloudStorageStream
    spec_class = SourceGoogleCloudStorageSpec
    documentation_url = "https://docs.airbyte.io/integrations/sources/google_cloud_storage"
