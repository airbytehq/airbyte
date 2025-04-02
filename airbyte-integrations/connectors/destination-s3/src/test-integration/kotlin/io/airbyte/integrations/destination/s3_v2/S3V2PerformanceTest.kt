/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.write.BasicPerformanceTest
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

@Disabled("We don't want this to run in CI")
class S3V2JsonNoFrillsPerformanceTest :
    BasicPerformanceTest(
        configContents = S3V2TestUtils.getConfig(S3V2TestUtils.JSON_UNCOMPRESSED_CONFIG_PATH),
        configSpecClass = S3V2Specification::class.java,
        defaultRecordsToInsert = 1_000_000,
        micronautProperties = S3V2TestUtils.PERFORMANCE_TEST_MICRONAUT_PROPERTIES,
        numFilesForFileTransfer = 5,
        fileSizeMbForFileTransfer = 1024,
    ) {
    @Test
    override fun testFileTransfer() {
        super.testFileTransfer()
    }
}

@Disabled("We don't want this to run in CI")
class S3V2ParquetSnappyPerformanceTest :
    BasicPerformanceTest(
        configContents = S3V2TestUtils.getConfig(S3V2TestUtils.PARQUET_SNAPPY_CONFIG_PATH),
        configSpecClass = S3V2Specification::class.java,
        defaultRecordsToInsert = 1_000_000,
        micronautProperties = S3V2TestUtils.PERFORMANCE_TEST_MICRONAUT_PROPERTIES,
    )
