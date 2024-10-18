/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import org.junit.jupiter.api.Test

class S3V2WriteTestJsonUncompressed :
    BasicFunctionalityIntegrationTest(
        S3V2TestUtils.getConfig(S3V2TestUtils.JSON_UNCOMPRESSED_CONFIG_PATH),
        S3V2DataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class S3V2WriteTestJsonGzip :
    BasicFunctionalityIntegrationTest(
        S3V2TestUtils.getConfig(S3V2TestUtils.JSON_GZIP_CONFIG_PATH),
        S3V2DataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}
