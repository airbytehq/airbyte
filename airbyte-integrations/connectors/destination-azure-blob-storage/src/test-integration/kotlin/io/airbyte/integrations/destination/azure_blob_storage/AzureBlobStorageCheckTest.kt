package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.check.CheckIntegrationTest

class AzureBlobStorageCheckTest :
    CheckIntegrationTest<AzureBlobStorageSpecification>(
        successConfigFilenames = emptyList(),
        failConfigFilenamesAndFailureReasons = emptyMap()
    )
