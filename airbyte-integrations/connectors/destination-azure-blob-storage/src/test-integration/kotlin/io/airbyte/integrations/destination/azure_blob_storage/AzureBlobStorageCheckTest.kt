package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig

class AzureBlobStorageCheckTest :
    CheckIntegrationTest<AzureBlobStorageSpecification>(
        successConfigFilenames = listOf(CheckTestConfig(AzureBlobStorageTestUtil.configPath)),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    )
