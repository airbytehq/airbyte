/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.testutils

import io.airbyte.cdk.db.factory.DSLContextFactory
import io.airbyte.cdk.db.factory.DataSourceFactory
import javax.sql.DataSource
import org.jooq.DSLContext
import org.jooq.SQLDialect
import org.testcontainers.containers.JdbcDatabaseContainer

/**
 * Helper class that facilitates the creation of database connection objects for testing purposes.
 */
object DatabaseConnectionHelper {
    /**
     * Constructs a new [DataSource] using the provided configuration.
     *
     * @param container A JDBC Test Container instance.
     * @return The configured [DataSource].
     */
    @JvmStatic
    fun createDataSource(container: JdbcDatabaseContainer<*>): DataSource {
        return DataSourceFactory.create(
            container.username,
            container.password,
            container.driverClassName,
            container.jdbcUrl
        )
    }

    /**
     * Constructs a configured [DSLContext] instance using the provided configuration.
     *
     * @param container A JDBC Test Container instance.
     * @param dialect The SQL dialect to use with objects created from this context.
     * @return The configured [DSLContext].
     */
    @JvmStatic
    fun createDslContext(container: JdbcDatabaseContainer<*>, dialect: SQLDialect?): DSLContext? {
        return DSLContextFactory.create(
            container.username,
            container.password,
            container.driverClassName,
            container.jdbcUrl,
            dialect
        )
    }
}
