/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.check.impl

import io.airbyte.cdk.db.factory.DSLContextFactory
import io.airbyte.cdk.db.factory.DataSourceFactory
import javax.sql.DataSource
import org.jooq.DSLContext
import org.jooq.SQLDialect
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.testcontainers.containers.PostgreSQLContainer

/** Common test setup for database availability check tests. */
internal class CommonDatabaseCheckTest {
    protected var container: PostgreSQLContainer<*>? = null

    protected var dataSource: DataSource? = null

    protected var dslContext: DSLContext? = null

    @BeforeEach
    fun setup() {
        container = PostgreSQLContainer<Nothing>("postgres:13-alpine")
        container!!.start()

        dataSource =
            DataSourceFactory.create(
                container!!.username,
                container!!.password,
                container!!.driverClassName,
                container!!.jdbcUrl
            )
        dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES)
    }

    @AfterEach
    @Throws(Exception::class)
    fun cleanup() {
        DataSourceFactory.close(dataSource)
        container!!.stop()
    }

    companion object {
        protected const val TIMEOUT_MS: Long = 500L
    }
}
