/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.command.object_storage.CSVFormatSpecification
import io.airbyte.cdk.load.command.object_storage.JsonFormatSpecification

class AzureBlobStorageCheckTest :
    CheckIntegrationTest<AzureBlobStorageSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(AzureBlobStorageTestUtil.getConfig(JsonFormatSpecification())),
                CheckTestConfig(AzureBlobStorageTestUtil.getConfig(CSVFormatSpecification()))
            ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    )
