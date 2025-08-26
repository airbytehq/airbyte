/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseConfigUpdater
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseContainerHelper
import io.airbyte.integrations.destination.clickhouse_v2.Utils.getConfigPath
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecification
import java.nio.file.Files
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled

@Disabled
class ClickhouseCheckTest :
    CheckIntegrationTest<ClickhouseSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(Files.readString(getConfigPath("valid_connection.json"))),
            ),
        failConfigFilenamesAndFailureReasons =
            mapOf(
                CheckTestConfig(
                    Files.readString(getConfigPath("non_valid_credentials_connection.json")),
                    name = "Non valid username and password",
                ) to
                    "Authentication failed: password is incorrect, or there is no user with such name".toPattern(),
                CheckTestConfig(
                    Files.readString(getConfigPath("non_valid_connection_host.json")),
                    name = "Non valid username and password",
                ) to
                    "Could not connect with provided configuration. Error: Failed to connect".toPattern(),
            ),
        configUpdater = ClickhouseConfigUpdater(),
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            ClickhouseContainerHelper.start()
        }
    }
}
