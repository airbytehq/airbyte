/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.databricks.spec.DatabricksSpecification
import io.airbyte.integrations.destination.databricks.write.CONFIG_PATH
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

/**
 * CDK-style check integration test for Databricks. Runs the `check` command through the full
 * connector process (black-box) using the CDK test harness.
 */
class DatabricksCheckTest :
    CheckIntegrationTest<DatabricksSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    configContents = Files.readString(Path.of(CONFIG_PATH)),
                ),
            ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    ) {

    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
