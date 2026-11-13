/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.redshift.config.RedshiftSpecification
import io.airbyte.integrations.destination.redshift.write.CONFIG_PATH
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

/**
 * CDK-style check integration test for Redshift. Runs the `check` command through the full
 * connector process (black-box) using the CDK test harness.
 *
 * This complements the existing [RedshiftCheckerTest] which tests the checker directly via JDBC.
 * This test verifies the check works end-to-end when invoked as the connector process.
 */
class RedshiftCheckTest :
    CheckIntegrationTest<RedshiftSpecification>(
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
