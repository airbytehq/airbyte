/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.mysql.MySQLConfigUpdater
import io.airbyte.integrations.destination.mysql.MySQLContainerHelper
import io.airbyte.integrations.destination.mysql.Utils.getConfigPath
import io.airbyte.integrations.destination.mysql.spec.MySQLSpecification
import java.nio.file.Files
import org.junit.jupiter.api.BeforeAll

class MySQLCheckTest :
    CheckIntegrationTest<MySQLSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(Files.readString(getConfigPath("valid_connection.json"))),
            ),
        failConfigFilenamesAndFailureReasons =
            mapOf(
                CheckTestConfig(
                    Files.readString(getConfigPath("invalid_credentials_connection.json")),
                    name = "Invalid username and password",
                ) to
                    "Access denied for user".toPattern(),
                CheckTestConfig(
                    Files.readString(getConfigPath("invalid_host_connection.json")),
                    name = "Invalid host",
                ) to
                    "Could not connect with provided configuration".toPattern(),
            ),
        configUpdater = MySQLConfigUpdater(),
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            MySQLContainerHelper.start()
        }
    }
}
