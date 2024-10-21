/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.factory

import io.airbyte.cdk.integrations.JdbcConnector
import org.jooq.SQLDialect
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Test suite for the [DSLContextFactory] class. */
internal class DSLContextFactoryTest : CommonFactoryTest() {
    @Test
    fun testCreatingADslContext() {
        val dataSource =
            DataSourceFactory.create(
                container.username,
                container.password,
                container.driverClassName,
                container.getJdbcUrl()
            )
        val dialect = SQLDialect.POSTGRES
        val dslContext = DSLContextFactory.create(dataSource, dialect)
        Assertions.assertNotNull(dslContext)
        Assertions.assertEquals(dialect, dslContext.configuration().dialect())
    }

    @Test
    fun testCreatingADslContextWithIndividualConfiguration() {
        val dialect = SQLDialect.POSTGRES
        val dslContext =
            DSLContextFactory.create(
                container.username,
                container.password,
                container.driverClassName,
                container.getJdbcUrl(),
                dialect
            )
        Assertions.assertNotNull(dslContext)
        Assertions.assertEquals(dialect, dslContext.configuration().dialect())
    }

    @Test
    fun testCreatingADslContextWithIndividualConfigurationAndConnectionProperties() {
        val connectionProperties = mapOf("foo" to "bar")
        val dialect = SQLDialect.POSTGRES
        val dslContext =
            DSLContextFactory.create(
                container.username,
                container.password,
                container.driverClassName,
                container.getJdbcUrl(),
                dialect,
                connectionProperties,
                JdbcConnector.CONNECT_TIMEOUT_DEFAULT
            )
        Assertions.assertNotNull(dslContext)
        Assertions.assertEquals(dialect, dslContext.configuration().dialect())
    }
}
