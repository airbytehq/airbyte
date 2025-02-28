/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLSpecification

class MSSQLBulkLoadCheckTest :
    CheckIntegrationTest<MSSQLSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    MSSQLTestConfigUtil.getConfigPath("secrets/bulk_upload_config.json"),
                    name = "Bulk Load Check Should work",
                ),
            ),
        emptyMap(),
        configUpdater = FakeConfigurationUpdater,
    )
