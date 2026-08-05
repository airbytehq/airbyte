/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks

import io.airbyte.integrations.destination.databricks.spec.CdcDeletionMode
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import io.airbyte.integrations.destination.databricks.spec.OAuthConfiguration
import io.airbyte.integrations.destination.databricks.spec.PersonalAccessTokenConfiguration
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class DatabricksBeanFactoryTest {

    private val beanFactory = DatabricksBeanFactory()

    @Test
    fun `PAT is passed to JDBC properties`() {
        val dataSource =
            beanFactory.databricksDataSource(
                config(PersonalAccessTokenConfiguration("test-token")),
            ) as com.databricks.client.jdbc.DataSource

        val tokenEntry =
            dataSource.properties.entries.firstOrNull {
                it.key.toString().equals("pwd", ignoreCase = true) ||
                    it.key.toString().equals("password", ignoreCase = true)
            } ?: error("JDBC token property was not set")

        assertEquals("test-token", tokenEntry.value)
        assertEquals("token", dataSource.properties.entries.first { it.key.toString().equals("uid", true) }.value)
        assertEquals("3", dataSource.properties.entries.first { it.key.toString().equals("authmech", true) }.value)
    }

    @Test
    fun `OAuth credentials are passed to JDBC properties`() {
        val dataSource =
            beanFactory.databricksDataSource(
                config(OAuthConfiguration("test-client-id", "test-secret")),
            ) as com.databricks.client.jdbc.DataSource

        assertEquals(
            "test-client-id",
            dataSource.properties.entries.first { it.key.toString().equals("oauth2clientid", true) }.value,
        )
        assertEquals(
            "test-secret",
            dataSource.properties.entries.first { it.key.toString().equals("oauth2secret", true) }.value,
        )
        assertEquals("11", dataSource.properties.entries.first { it.key.toString().equals("authmech", true) }.value)
        assertEquals("1", dataSource.properties.entries.first { it.key.toString().equals("auth_flow", true) }.value)
    }

    private fun config(authType: io.airbyte.integrations.destination.databricks.spec.DatabricksAuthConfiguration) =
        DatabricksConfiguration(
            hostname = "test.cloud.databricks.com",
            httpPath = "/sql/1.0/warehouses/test",
            port = "443",
            database = "test_catalog",
            schema = "test_schema",
            authType = authType,
            purgeStagingData = true,
            acceptTerms = true,
            cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
        )
}
