/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.command.object_storage.CSVFormatSpecification
import io.airbyte.cdk.load.command.object_storage.FlatteningSpecificationProvider.Flattening
import io.airbyte.cdk.load.command.object_storage.JsonFormatSpecification
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import org.junit.jupiter.api.Test

abstract class AzureBlobStorageWriteTest(configContents: String) :
    BasicFunctionalityIntegrationTest(
        configContents = configContents,
        configSpecClass = AzureBlobStorageSpecification::class.java,
        dataDumper = AzureBlobStorageDataDumper(),
        recordMangler = UncoercedExpectedRecordMapper,
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
    )

class AzureBlobStorageCsvNoFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getConfig(
            CSVFormatSpecification(flattening = Flattening.NO_FLATTENING)
        )
    ) {
    @Test
    override fun testBasicWriteFile() {
        super.testBasicWriteFile()
    }

    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class AzureBlobStorageCsvWithFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getConfig(
            CSVFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING)
        )
    )

class AzureBlobStorageJsonlNoFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getConfig(
            JsonFormatSpecification(flattening = Flattening.NO_FLATTENING)
        )
    )

class AzureBlobStorageJsonlWithFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getConfig(
            JsonFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING)
        )
    )
