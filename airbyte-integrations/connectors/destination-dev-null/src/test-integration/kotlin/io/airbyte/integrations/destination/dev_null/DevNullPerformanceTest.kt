/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.write.BasicPerformanceTest
import org.junit.jupiter.api.Test

class DevNullPerformanceTest :
    BasicPerformanceTest(
        configContents = DevNullTestUtils.loggingConfigContents,
        configSpecClass = DevNullSpecification::class.java,
        defaultRecordsToInsert = 1000000,
    ) {
    @Test
    override fun testInsertRecords() {
        testInsertRecords { summary -> assert(summary[0].recordPerSeconds > 1000) }
    }
}
