/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import org.junit.jupiter.api.Test

class BigQueryCheckTest :
    CheckIntegrationTest<BigquerySpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(BigQueryDestinationTestUtils.standardInsertConfig),
            ),
        failConfigFilenamesAndFailureReasons = mapOf(),
        additionalMicronautEnvs = additionalMicronautEnvs,
    ) {
    @Test
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
