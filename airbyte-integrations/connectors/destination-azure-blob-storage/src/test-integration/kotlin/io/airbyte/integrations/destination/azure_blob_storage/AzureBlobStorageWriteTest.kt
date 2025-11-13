/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.command.object_storage.CSVFormatSpecification
import io.airbyte.cdk.load.command.object_storage.FlatteningSpecificationProvider.Flattening
import io.airbyte.cdk.load.command.object_storage.JsonFormatSpecification
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.cdk.load.write.Untyped
import org.junit.jupiter.api.Disabled

abstract class AzureBlobStorageWriteTest(
    configContents: String,
    nullEqualsUnset: Boolean = true,
    mismatchedTypesUnrepresentable: Boolean = false,
    unknownTypesBehavior: UnknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
    dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL
) :
    BasicFunctionalityIntegrationTest(
        configContents = configContents,
        configSpecClass = AzureBlobStorageSpecification::class.java,
        dataDumper = AzureBlobStorageDataDumper(),
        recordMangler = UncoercedExpectedRecordMapper,
        destinationCleaner = NoopDestinationCleaner,
        isStreamSchemaRetroactive = false,
        dedupBehavior = null,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        supportFileTransfer = true,
        commitDataIncrementally = true,
        allTypesBehavior = Untyped,
        nullEqualsUnset = nullEqualsUnset,
        unknownTypesBehavior = unknownTypesBehavior,
        mismatchedTypesUnrepresentable = mismatchedTypesUnrepresentable,
        dataChannelMedium = dataChannelMedium,
        dataChannelFormat = dataChannelFormat,
    )

class AzureBlobStorageCsvNoFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            CSVFormatSpecification(flattening = Flattening.NO_FLATTENING)
        ),
    )

class AzureBlobStorageCsvNoFlatteningWriteTestProto :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            CSVFormatSpecification(flattening = Flattening.NO_FLATTENING),
        ),
        nullEqualsUnset = true,
        mismatchedTypesUnrepresentable = true,
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
    ) {
    @Disabled("Not relevant for socket mode")
    override fun testBasicWriteFile() {
        super.testBasicWriteFile()
    }
}

class AzureBlobStorageCsvWithFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            CSVFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING)
        ),
    )

class AzureBlobStorageCsvWithFlatteningWriteTestProto :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            CSVFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING),
        ),
        nullEqualsUnset = true,
        mismatchedTypesUnrepresentable = true,
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
    ) {
    @Disabled("Not relevant for socket mode")
    override fun testBasicWriteFile() {
        super.testBasicWriteFile()
    }
}

class AzureBlobStorageJsonlNoFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            JsonFormatSpecification(flattening = Flattening.NO_FLATTENING)
        ),
    )

class AzureBlobStorageJsonlNoFlatteningWriteTestProto :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            JsonFormatSpecification(flattening = Flattening.NO_FLATTENING),
        ),
        nullEqualsUnset = true,
        mismatchedTypesUnrepresentable = true,
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
    ) {
    @Disabled("Not relevant for socket mode")
    override fun testBasicWriteFile() {
        super.testBasicWriteFile()
    }
}

class AzureBlobStorageJsonlWithFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            JsonFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING)
        ),
    )

class AzureBlobStorageJsonlWithFlatteningWriteTestProto :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getAccountKeyConfig(
            JsonFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING),
        ),
        nullEqualsUnset = true,
        mismatchedTypesUnrepresentable = true,
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
    ) {
    @Disabled("Not relevant for socket mode")
    override fun testBasicWriteFile() {
        super.testBasicWriteFile()
    }
}

class AzureBlobStorageSasCsvWithFlatteningWriteTest :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getSasConfig(
            CSVFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING)
        ),
    )

class AzureBlobStorageSasCsvWithFlatteningWriteTestProto :
    AzureBlobStorageWriteTest(
        AzureBlobStorageTestUtil.getSasConfig(
            CSVFormatSpecification(flattening = Flattening.ROOT_LEVEL_FLATTENING),
        ),
        nullEqualsUnset = true,
        mismatchedTypesUnrepresentable = true,
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
    ) {
    @Disabled("Not relevant for socket mode")
    override fun testBasicWriteFile() {
        super.testBasicWriteFile()
    }
}
