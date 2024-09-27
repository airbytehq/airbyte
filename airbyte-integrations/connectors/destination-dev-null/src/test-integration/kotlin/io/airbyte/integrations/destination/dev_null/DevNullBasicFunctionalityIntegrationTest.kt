/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.test.spec.SpecTest
import io.airbyte.cdk.test.util.NoopDestinationCleaner
import io.airbyte.cdk.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.test.write.BasicFunctionalityIntegrationTest
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
    override fun testCheck() {
        super.testCheck()
    }

    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class DevNullSpecTest : SpecTest()
