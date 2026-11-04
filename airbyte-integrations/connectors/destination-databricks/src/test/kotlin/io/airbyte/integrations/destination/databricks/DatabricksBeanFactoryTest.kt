/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks

import com.databricks.client.jdbc.DataSource
import io.airbyte.integrations.destination.databricks.spec.CdcDeletionMode
import io.airbyte.integrations.destination.databricks.spec.DatabricksAuthConfiguration
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
            ) as DataSource

        assertEquals("test-token", dataSource.property("pwd", "password"))
        assertEquals("token", dataSource.property("uid"))
        assertEquals("3", dataSource.property("authmech"))
    }

    @Test
    fun `OAuth credentials are passed to JDBC properties`() {
        val dataSource =
            beanFactory.databricksDataSource(
                config(OAuthConfiguration("test-client-id", "test-secret")),
            ) as DataSource

        assertEquals("test-client-id", dataSource.property("oauth2clientid"))
        assertEquals("test-secret", dataSource.property("oauth2secret"))
        assertEquals("11", dataSource.property("authmech"))
        assertEquals("1", dataSource.property("auth_flow"))
    }

    private fun DataSource.property(vararg names: String): Any =
        properties.entries
            .first { entry -> names.any { it.equals(entry.key.toString(), ignoreCase = true) } }
            .value

    private fun config(authType: DatabricksAuthConfiguration) =
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
