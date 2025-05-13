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

abstract class AzureBlobStorageWriteTest(
    configContents: String,
    preserveUndeclaredFields: Boolean = true,
    nullEqualsUnset: Boolean,
) :
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
        preserveUndeclaredFields = preserveUndeclaredFields,
        supportFileTransfer = true,
        commitDataIncrementally = true,
        allTypesBehavior = Untyped,
        nullEqualsUnset = nullEqualsUnset,
    )

class AzureBlobStorageCsvNoFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            CSVFormatSpecification(flattening = Flattening.NO_FLATTENING)
        ),
        nullEqualsUnset = true,
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
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            CSVFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING)
        ),
        preserveUndeclaredFields = false,
        nullEqualsUnset = true,
    )

class AzureBlobStorageJsonlNoFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            JsonFormatSpecification(flattening = Flattening.NO_FLATTENING)
        ),
        nullEqualsUnset = false,
    )

class AzureBlobStorageJsonlWithFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            JsonFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING)
        ),
        nullEqualsUnset = false,
    )

class AzureBlobStorageSasCsvWithFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getSasConfig(
            CSVFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING)
        ),
        preserveUndeclaredFields = false,
        nullEqualsUnset = true,
    )
