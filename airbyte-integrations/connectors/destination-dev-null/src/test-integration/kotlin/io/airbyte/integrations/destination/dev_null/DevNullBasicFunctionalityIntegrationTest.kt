/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import org.junit.jupiter.api.Test

class DevNullBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        DevNullTestUtils.loggingConfig,
        DevNullDestinationDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        verifyDataWriting = false,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Test
    override fun testMidSyncCheckpointingStreamState() {
        super.testMidSyncCheckpointingStreamState()
    }
}
