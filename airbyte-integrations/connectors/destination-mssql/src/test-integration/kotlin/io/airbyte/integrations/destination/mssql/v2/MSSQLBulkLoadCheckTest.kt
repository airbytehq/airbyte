/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLSpecification
import java.nio.file.Files
import java.nio.file.Path

class MSSQLBulkLoadCheckTest :
    CheckIntegrationTest<MSSQLSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    Files.readString(Path.of(CONFIG_FILE)),
                    name = "Azure Bulk Load Check should work",
                ),
            ),
        emptyMap(),
        configUpdater = FakeConfigurationUpdater,
    ) {
    companion object {
        const val CONFIG_FILE = "secrets/azure_bulk_config.json"
    }
}
