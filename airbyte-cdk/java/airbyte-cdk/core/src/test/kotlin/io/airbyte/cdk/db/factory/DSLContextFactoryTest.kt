/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.factory

import io.airbyte.cdk.integrations.JdbcConnector
import java.util.Map
import org.jooq.SQLDialect
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Test suite for the [DSLContextFactory] class. */
internal class DSLContextFactoryTest : CommonFactoryTest() {
    @Test
    fun testCreatingADslContext() {
        val dataSource =
            DataSourceFactory.create(
                CommonFactoryTest.Companion.container!!.getUsername(),
                CommonFactoryTest.Companion.container!!.getPassword(),
                CommonFactoryTest.Companion.container!!.getDriverClassName(),
                CommonFactoryTest.Companion.container!!.getJdbcUrl()
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
                CommonFactoryTest.Companion.container!!.getUsername(),
                CommonFactoryTest.Companion.container!!.getPassword(),
                CommonFactoryTest.Companion.container!!.getDriverClassName(),
                CommonFactoryTest.Companion.container!!.getJdbcUrl(),
                dialect
            )
        Assertions.assertNotNull(dslContext)
        Assertions.assertEquals(dialect, dslContext.configuration().dialect())
    }

    @Test
    fun testCreatingADslContextWithIndividualConfigurationAndConnectionProperties() {
        val connectionProperties = Map.of("foo", "bar")
        val dialect = SQLDialect.POSTGRES
        val dslContext =
            DSLContextFactory.create(
                CommonFactoryTest.Companion.container!!.getUsername(),
                CommonFactoryTest.Companion.container!!.getPassword(),
                CommonFactoryTest.Companion.container!!.getDriverClassName(),
                CommonFactoryTest.Companion.container!!.getJdbcUrl(),
                dialect,
                connectionProperties,
                JdbcConnector.CONNECT_TIMEOUT_DEFAULT
            )
        Assertions.assertNotNull(dslContext)
        Assertions.assertEquals(dialect, dslContext.configuration().dialect())
    }
}
