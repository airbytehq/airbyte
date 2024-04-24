/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.testutils

import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.testutils.DatabaseConnectionHelper.createDataSource
import io.airbyte.cdk.testutils.DatabaseConnectionHelper.createDslContext
import org.jooq.SQLDialect
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.PostgreSQLContainer

internal class DatabaseConnectionHelperTest {
    @Test
    fun testCreatingFromATestContainer() {
        val dataSource = createDataSource(container)
        Assertions.assertNotNull(dataSource)
        Assertions.assertEquals(HikariDataSource::class.java, dataSource.javaClass)
        Assertions.assertEquals(
            10,
            (dataSource as HikariDataSource?)!!.hikariConfigMXBean.maximumPoolSize
        )
    }

    @Test
    fun testCreatingADslContextFromATestContainer() {
        val dialect = SQLDialect.POSTGRES
        val dslContext = createDslContext(container, dialect)
        Assertions.assertNotNull(dslContext)
        Assertions.assertEquals(dialect, dslContext!!.configuration().dialect())
    }

    companion object {
        private const val DATABASE_NAME = "airbyte_test_database"

        protected var container: PostgreSQLContainer<*> =
            PostgreSQLContainer("postgres:13-alpine")
                .withDatabaseName(DATABASE_NAME)
                .withUsername("docker")
                .withPassword("docker")

        @BeforeAll
        @JvmStatic
        fun dbSetup() {
            container.start()
        }

        @AfterAll
        @JvmStatic
        fun dbDown() {
            container.close()
        }
    }
}
