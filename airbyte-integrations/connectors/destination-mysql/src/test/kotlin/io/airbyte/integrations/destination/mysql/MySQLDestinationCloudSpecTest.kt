/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlagsWrapper
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class MySQLDestinationCloudSpecTest {
    private fun cloudDestination(): SshWrappedDestination =
        SshWrappedDestination(
            MySQLDestination(
                FeatureFlagsWrapper.overridingDeploymentMode(
                    EnvVariableFeatureFlags(),
                    AdaptiveSourceRunner.CLOUD_MODE
                )
            ),
            JdbcUtils.HOST_LIST_KEY,
            JdbcUtils.PORT_LIST_KEY
        )

    @Test
    fun testCloudSpecMatchesExpected() {
        val expected =
            Jsons.deserialize(
                MoreResources.readResource("expected_cloud_spec.json"),
                ConnectorSpecification::class.java
            )
        Assertions.assertEquals(expected, cloudDestination().spec())
    }

    @Test
    fun testCloudSpecOmitsSslOption() {
        Assertions.assertFalse(
            cloudDestination().spec().connectionSpecification["properties"].has(JdbcUtils.SSL_KEY)
        )
    }

    @Test
    fun testOssSpecKeepsSslOption() {
        Assertions.assertTrue(
            MySQLDestination().spec().connectionSpecification["properties"].has(JdbcUtils.SSL_KEY)
        )
    }

    @Test
    fun testCloudModeAlwaysUsesSslConnectionProperties() {
        val config =
            Jsons.jsonNode(
                mapOf(
                    JdbcUtils.HOST_KEY to "localhost",
                    JdbcUtils.PORT_KEY to 3306,
                    JdbcUtils.USERNAME_KEY to "user",
                    JdbcUtils.DATABASE_KEY to "db",
                    JdbcUtils.SSL_KEY to false
                )
            )
        val cloudDestination =
            MySQLDestination(
                FeatureFlagsWrapper.overridingDeploymentMode(
                    EnvVariableFeatureFlags(),
                    AdaptiveSourceRunner.CLOUD_MODE
                )
            )
        Assertions.assertEquals(
            MySQLDestination.DEFAULT_SSL_JDBC_PARAMETERS,
            cloudDestination.getDefaultConnectionProperties(config)
        )
        Assertions.assertEquals(
            MySQLDestination.DEFAULT_JDBC_PARAMETERS,
            MySQLDestination().getDefaultConnectionProperties(config)
        )
    }
}
