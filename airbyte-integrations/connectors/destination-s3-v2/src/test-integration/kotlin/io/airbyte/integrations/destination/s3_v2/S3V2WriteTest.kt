/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.Test

abstract class S3V2WriteTest(path: String) :
    BasicFunctionalityIntegrationTest(
        S3V2TestUtils.getConfig(path),
        S3V2DataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
    ) {
    private val log = KotlinLogging.logger {}

    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Test
    override fun testMidSyncCheckpointingStreamState() {
        log.warn { "Disabled until it doesn't block." }
    }
}

class S3V2WriteTestJsonUncompressed : S3V2WriteTest(S3V2TestUtils.JSON_UNCOMPRESSED_CONFIG_PATH)

class S3V2WriteTestJsonGzip : S3V2WriteTest(S3V2TestUtils.JSON_GZIP_CONFIG_PATH)

class S3V2WriteTestCsvUncompressed : S3V2WriteTest(S3V2TestUtils.CSV_UNCOMPRESSED_CONFIG_PATH)

class S3V2WriteTestCsvGzip : S3V2WriteTest(S3V2TestUtils.CSV_GZIP_CONFIG_PATH)
