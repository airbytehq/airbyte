/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLSpecification
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.TestInstance

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
internal class MSSQLCheckTest :
    CheckIntegrationTest<MSSQLSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(MSSQLTestConfigUtil.getConfigPath("check/valid.json")),
                CheckTestConfig(MSSQLTestConfigUtil.getConfigPath("check/valid-ssl-trust.json")),
            ),
        failConfigFilenamesAndFailureReasons =
            mapOf(
                CheckTestConfig(
                    MSSQLTestConfigUtil.getConfigPath("check/fail-internal-schema-invalid.json")
                ) to "\"iamnotthere\" either does not exist".toPattern(),
            ),
        configUpdater = MSSQLContainerHelper
    ) {

    @BeforeAll
    fun beforeAll() {
        MSSQLContainerHelper.start()
    }

    @AfterAll
    fun afterAll() {
        MSSQLContainerHelper.stop()
    }
}
