/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

abstract class S3V2WriteTest(path: String) :
    BasicFunctionalityIntegrationTest(
        S3V2TestUtils.getConfig(path),
        S3V2Specification::class.java,
        S3V2DataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        isStreamSchemaRetroactive = false,
        supportsDedup = false,
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

    @Disabled("append mode doesn't yet work")
    @Test
    override fun testAppend() {
        super.testAppend()
    }

    @Disabled("append mode doesn't yet work")
    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }
}

class S3V2WriteTestJsonUncompressed : S3V2WriteTest(S3V2TestUtils.JSON_UNCOMPRESSED_CONFIG_PATH)

class S3V2WriteTestJsonGzip : S3V2WriteTest(S3V2TestUtils.JSON_GZIP_CONFIG_PATH)

class S3V2WriteTestCsvUncompressed : S3V2WriteTest(S3V2TestUtils.CSV_UNCOMPRESSED_CONFIG_PATH)

class S3V2WriteTestCsvGzip : S3V2WriteTest(S3V2TestUtils.CSV_GZIP_CONFIG_PATH)

class S3V2WriteTestAvroUncompressed : S3V2WriteTest(S3V2TestUtils.AVRO_UNCOMPRESSED_CONFIG_PATH)

class S3V2WriteTestAvroBzip2 : S3V2WriteTest(S3V2TestUtils.AVRO_BZIP2_CONFIG_PATH)

class S3V2WriteTestParquetUncompressed :
    S3V2WriteTest(S3V2TestUtils.PARQUET_UNCOMPRESSED_CONFIG_PATH)

class S3V2WriteTestParquetSnappy : S3V2WriteTest(S3V2TestUtils.PARQUET_SNAPPY_CONFIG_PATH)
