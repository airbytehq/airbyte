package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLSpecification

class MSSQLCheckTest : CheckIntegrationTest<MSSQLSpecification>(
    successConfigFilenames = listOf(
        CheckTestConfig(MSSQLTestConfigUtil.getConfigPath("check/valid.json")),
    ),
    failConfigFilenamesAndFailureReasons = emptyMap()
) {
}
