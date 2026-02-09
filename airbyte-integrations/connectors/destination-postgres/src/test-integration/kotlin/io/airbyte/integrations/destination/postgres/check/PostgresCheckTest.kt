/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.postgres.PostgresConfigUpdater
import io.airbyte.integrations.destination.postgres.PostgresContainerHelper
import io.airbyte.integrations.destination.postgres.spec.PostgresSpecification
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class PostgresCheckTest :
    CheckIntegrationTest<PostgresSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    configContents =
                        """{
                        "host": "replace_me_host",
                        "port": replace_me_port,
                        "database": "replace_me_database",
                        "schema": "public",
                        "username": "replace_me_username",
                        "password": "replace_me_password"
                    }""",
                ),
            ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
        configUpdater = PostgresConfigUpdater(),
    ) {

    companion object {
        @JvmStatic
        @BeforeAll
        fun startContainer() {
            PostgresContainerHelper.start()
        }
        // Note: Don't stop the container here - other tests running in parallel may still need it.
        // Testcontainers will clean up automatically when the JVM exits.
    }

    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
