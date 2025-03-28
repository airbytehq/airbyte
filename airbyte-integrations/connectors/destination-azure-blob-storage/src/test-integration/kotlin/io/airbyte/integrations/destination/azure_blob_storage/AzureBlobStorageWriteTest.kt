/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled

abstract class AzureBlobStorageWriteTest(configContents: String) :
    BasicFunctionalityIntegrationTest(
        configContents = configContents,
        configSpecClass = AzureBlobStorageSpecification::class.java,
        dataDumper = AzureBlobStorageDataDumper(),
        destinationCleaner = NoopDestinationCleaner,
        isStreamSchemaRetroactive = false,
        supportsDedup = false,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        supportFileTransfer = true,
        commitDataIncrementally = true,
        allTypesBehavior = Untyped,
    ) {
    companion object {
        @BeforeAll
        @JvmStatic
        fun setup() {
            AzureBlobStorageTestContainer.start()
        }
    }
}

@Disabled class AzureBlobStorageCsvWriteTest : AzureBlobStorageWriteTest(TODO())

@Disabled class AzureBlobStorageJsonlWriteTest : AzureBlobStorageWriteTest(TODO())
