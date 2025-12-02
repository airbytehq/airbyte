/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.factory

import java.time.Duration
import javax.sql.DataSource
import org.jooq.DSLContext
import org.jooq.SQLDialect
import org.jooq.impl.DSL

/**
 * Temporary factory class that provides convenience methods for creating a [DSLContext] instances.
 * This class will be removed once the project has been converted to leverage an application
 * framework to manage the creation and injection of [DSLContext] objects.
 */
object DSLContextFactory {
    /**
     * Constructs a configured [DSLContext] instance using the provided configuration.
     *
     * @param dataSource The [DataSource] used to connect to the database.
     * @param dialect The SQL dialect to use with objects created from this context.
     * @return The configured [DSLContext].
     */
    fun create(dataSource: DataSource?, dialect: SQLDialect?): DSLContext {
        return DSL.using(dataSource, dialect)
    }

    /**
     * Constructs a configured [DSLContext] instance using the provided configuration.
     *
     * @param username The username of the database user.
     * @param password The password of the database user.
     * @param driverClassName The fully qualified name of the JDBC driver class.
     * @param jdbcConnectionString The JDBC connection string.
     * @param dialect The SQL dialect to use with objects created from this context.
     * @return The configured [DSLContext].
     */
    @JvmStatic
    fun create(
        username: String?,
        password: String?,
        driverClassName: String,
        jdbcConnectionString: String?,
        dialect: SQLDialect?
    ): DSLContext {
        return DSL.using(
            DataSourceFactory.create(username, password, driverClassName, jdbcConnectionString),
            dialect
        )
    }

    /**
     * Constructs a configured [DSLContext] instance using the provided configuration.
     *
     * @param username The username of the database user.
     * @param password The password of the database user.
     * @param driverClassName The fully qualified name of the JDBC driver class.
     * @param jdbcConnectionString The JDBC connection string.
     * @param dialect The SQL dialect to use with objects created from this context.
     * @param connectionProperties Additional configuration properties for the underlying driver.
     * @return The configured [DSLContext].
     */
    fun create(
        username: String?,
        password: String?,
        driverClassName: String,
        jdbcConnectionString: String?,
        dialect: SQLDialect?,
        connectionProperties: Map<String, String>?,
        connectionTimeout: Duration?
    ): DSLContext {
        return DSL.using(
            DataSourceFactory.create(
                username,
                password,
                driverClassName,
                jdbcConnectionString,
                connectionProperties,
                connectionTimeout
            ),
            dialect
        )
    }
}
