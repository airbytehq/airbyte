#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.abstract_files_source import AbstractFilesSource
from source_s3_new.spec import SourceS3NewSpec
from source_s3_new.stream import S3NewStream


class SourceS3New(AbstractFilesSource):
    stream_class = S3NewStream
    spec_class = SourceS3NewSpec
    documentation_url = "https://docs.airbyte.io/integrations/sources/s3_new"
