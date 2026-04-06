/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.redshift2.RedshiftTestConfigProvider
import io.airbyte.integrations.destination.redshift2.config.RedshiftSpecification
import java.util.concurrent.TimeUnit
import java.util.regex.Pattern
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

/**
 * Integration tests for Redshift connection validation.
 * 
 * Tests verify that the connection check properly:
 * - Succeeds with valid credentials
 * - Fails with appropriate error messages for invalid credentials
 * - Handles incorrect host, database, username, and password scenarios
 */
class RedshiftConnectionTest :
    CheckIntegrationTest<RedshiftSpecification>(
        successConfigFilenames =
            if (RedshiftTestConfigProvider.hasValidConfig()) {
                listOf(
                    CheckTestConfig(
                        configContents = RedshiftTestConfigProvider.getValidConfig(),
                        name = "valid_redshift_config"
                    )
                )
            } else {
                emptyList()
            },
        failConfigFilenamesAndFailureReasons =
            if (RedshiftTestConfigProvider.hasValidConfig()) {
                mapOf(
                    CheckTestConfig(
                        configContents = RedshiftTestConfigProvider.getConfigWithIncorrectPassword(),
                        name = "incorrect_password"
                    ) to Pattern.compile("State code: 28.*", Pattern.DOTALL),
                    
                    CheckTestConfig(
                        configContents = RedshiftTestConfigProvider.getConfigWithIncorrectUsername(),
                        name = "incorrect_username"
                    ) to Pattern.compile("State code: 28.*", Pattern.DOTALL),
                    
                    CheckTestConfig(
                        configContents = RedshiftTestConfigProvider.getConfigWithIncorrectHost(),
                        name = "incorrect_host"
                    ) to Pattern.compile("State code: 08.*", Pattern.DOTALL),
                    
                    CheckTestConfig(
                        configContents = RedshiftTestConfigProvider.getConfigWithIncorrectDatabase(),
                        name = "incorrect_database"
                    ) to Pattern.compile("State code: 3D.*", Pattern.DOTALL),
                )
            } else {
                emptyMap()
            }
    ) {

    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testSuccessConfigs() {
        if (RedshiftTestConfigProvider.hasValidConfig()) {
            super.testSuccessConfigs()
        } else {
            println("Skipping testSuccessConfigs - no valid Redshift config available at secrets/config.json")
        }
    }

    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testFailConfigs() {
        if (RedshiftTestConfigProvider.hasValidConfig()) {
            super.testFailConfigs()
        } else {
            println("Skipping testFailConfigs - no valid Redshift config available at secrets/config.json")
        }
    }
}
