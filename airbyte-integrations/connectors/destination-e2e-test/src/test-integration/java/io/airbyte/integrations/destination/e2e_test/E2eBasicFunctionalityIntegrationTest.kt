/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test

import io.airbyte.cdk.test.util.NoopDestinationCleaner
import io.airbyte.cdk.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.test.write.BasicFunctionalityIntegrationTest
import org.junit.jupiter.api.Test

class E2eBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        E2eTestUtils.loggingConfig,
        E2eDestinationDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        verifyDataWriting = false,
    ) {
    @Test
    override fun testCheck() {
        super.testCheck()
    }

    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}
