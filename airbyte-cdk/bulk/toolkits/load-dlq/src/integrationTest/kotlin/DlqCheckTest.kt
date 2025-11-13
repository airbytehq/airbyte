/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.integrationTest.DLQ_INTEGRATION_TEST_ENV
import io.airbyte.cdk.load.integrationTest.DlqTestSpec

class DlqCheckTest :
    CheckIntegrationTest<DlqTestSpec>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    configContents =
                        """
                {
                    "object_storage_config":{
                        "storage_type":"None"
                    }
                }
            """.trimIndent(),
                    name = "No Object Storage Config",
                ),
                // TODO, this should become an automated tests, however, the existing tooling is
                // hardcoded to only pull credentials for a connector, not cdk/toolkits.
                //        CheckTestConfig(
                //            configContents = """
                //                {
                //                    "object_storage_config":{
                //                        "storage_type":"S3",
                //                        "format":{"format_type":"CSV","flattening":"Root level
                // flattening"},
                //
                // "file_name_format":"{sync_id}-{part_number}-{date}{format_extension}",
                //                        "path_format":"{sync_id}/{namespace}/{stream_name}/",
                //                        "s3_bucket_region":"us-east-2",
                //                        "s3_bucket_name":"dlq-toolkit",
                //                        "bucket_path":"rejected-records"
                //                    }
                //                }
                //            """.trimIndent(),
                //            name = "S3 Object Storage Config",
                //        ),
                ),
        failConfigFilenamesAndFailureReasons =
            mapOf(
                CheckTestConfig(
                    configContents =
                        """
                {
                    "object_storage_config":{
                        "storage_type":"S3",
                        "format":{"format_type":"CSV","flattening":"Root level flattening"},
                        "bucket_path":"destination-shelby",
                        "file_name_format":"{sync_id}-{part_number}-{date}{format_extension}",
                        "path_format":"{namespace}/{stream_name}/",
                        "s3_bucket_name":"yolo",
                        "s3_bucket_region":"us-west-1"
                    }
                }
            """.trimIndent(),
                    name = "S3 Object Storage Config without Credentials",
                ) to "Could not connect with provided configuration".toPattern(),
            ),
        additionalMicronautEnvs = listOf(DLQ_INTEGRATION_TEST_ENV, "aws"),
    ) {}
