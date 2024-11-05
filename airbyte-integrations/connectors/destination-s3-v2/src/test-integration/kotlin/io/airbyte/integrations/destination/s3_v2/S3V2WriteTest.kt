/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

abstract class S3V2WriteTest(
    path: String,
    stringifySchemalessObjects: Boolean,
    promoteUnionToObject: Boolean,
    preserveUndeclaredFields: Boolean,
    /** This is false for staging mode, and true for non-staging mode. */
    commitDataIncrementally: Boolean = false,
) :
    BasicFunctionalityIntegrationTest(
        S3V2TestUtils.getConfig(path),
        S3V2Specification::class.java,
        S3V2DataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        isStreamSchemaRetroactive = false,
        supportsDedup = false,
        stringifySchemalessObjects = stringifySchemalessObjects,
        promoteUnionToObject = promoteUnionToObject,
        preserveUndeclaredFields = preserveUndeclaredFields,
        commitDataIncrementally = commitDataIncrementally,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Test
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

    @Disabled
    @Test
    override fun testMidSyncCheckpointingStreamState() {
        super.testMidSyncCheckpointingStreamState()
    }

    @Test
    override fun testAppend() {
        super.testAppend()
    }

    @Disabled("append mode doesn't yet work")
    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

    @Test
    override fun testTruncateRefresh() {
        super.testTruncateRefresh()
    }

    @Test
    override fun testContainerTypes() {
        super.testContainerTypes()
    }

    @Test
    override fun testUnions() {
        super.testUnions()
    }

    @Disabled("connector doesn't yet do refreshes correctly - data from failed sync is lost")
    @Test
    override fun testInterruptedTruncateWithPriorData() {
        super.testInterruptedTruncateWithPriorData()
    }

    @Disabled("connector doesn't yet do refreshes correctly - failed sync deletes old data")
    @Test
    override fun resumeAfterCancelledTruncate() {
        super.resumeAfterCancelledTruncate()
    }

    @Disabled("connector doesn't yet do refreshes correctly - failed sync deletes old data")
    @Test
    override fun testInterruptedTruncateWithoutPriorData() {
        super.testInterruptedTruncateWithoutPriorData()
    }
}

class S3V2WriteTestJsonUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.JSON_UNCOMPRESSED_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
    )

class S3V2WriteTestJsonStaging :
    S3V2WriteTest(
        S3V2TestUtils.JSON_STAGING_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
    )

class S3V2WriteTestJsonGzip :
    S3V2WriteTest(
        S3V2TestUtils.JSON_GZIP_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
    )

class S3V2WriteTestCsvUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.CSV_UNCOMPRESSED_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
    )

class S3V2WriteTestCsvGzip :
    S3V2WriteTest(
        S3V2TestUtils.CSV_GZIP_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
    )

class S3V2WriteTestAvroUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.AVRO_UNCOMPRESSED_CONFIG_PATH,
        stringifySchemalessObjects = true,
        promoteUnionToObject = false,
        preserveUndeclaredFields = false,
    ) {
    @Disabled("Not yet working")
    @Test
    override fun testContainerTypes() {
        super.testContainerTypes()
    }

    @Disabled("Not yet working")
    @Test
    override fun testUnions() {
        super.testUnions()
    }
}

class S3V2WriteTestAvroBzip2 :
    S3V2WriteTest(
        S3V2TestUtils.AVRO_BZIP2_CONFIG_PATH,
        stringifySchemalessObjects = true,
        promoteUnionToObject = false,
        preserveUndeclaredFields = false,
    ) {
    @Disabled("Not yet working")
    @Test
    override fun testContainerTypes() {
        super.testContainerTypes()
    }

    @Disabled("Not yet working")
    @Test
    override fun testUnions() {
        super.testUnions()
    }
}

class S3V2WriteTestParquetUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.PARQUET_UNCOMPRESSED_CONFIG_PATH,
        stringifySchemalessObjects = true,
        promoteUnionToObject = true,
        preserveUndeclaredFields = false,
    ) {
    @Disabled("Not yet working")
    @Test
    override fun testContainerTypes() {
        super.testContainerTypes()
    }

    @Disabled("Not yet working")
    @Test
    override fun testUnions() {
        super.testUnions()
    }
}

class S3V2WriteTestParquetSnappy :
    S3V2WriteTest(
        S3V2TestUtils.PARQUET_SNAPPY_CONFIG_PATH,
        stringifySchemalessObjects = true,
        promoteUnionToObject = true,
        preserveUndeclaredFields = false,
    ) {
    @Disabled("Not yet working")
    @Test
    override fun testContainerTypes() {
        super.testContainerTypes()
    }

    @Disabled("Not yet working")
    @Test
    override fun testUnions() {
        super.testUnions()
    }
}
