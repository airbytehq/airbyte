/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.google.common.base.Preconditions
import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import java.time.Duration
import javax.sql.DataSource

/**
 * Temporary factory class that provides convenience methods for creating a [DataSource] instance.
 * This class will be removed once the project has been converted to leverage an application
 * framework to manage the creation and injection of [DataSource] objects.
 */
object DataSourceFactory {
    /**
     * Constructs a new [DataSource] using the provided configuration.
     *
     * @param username The username of the database user.
     * @param password The password of the database user.
     * @param driverClassName The fully qualified name of the JDBC driver class.
     * @param jdbcConnectionString The JDBC connection string.
     * @return The configured [DataSource].
     */
    @JvmStatic
    fun create(
        username: String?,
        password: String?,
        driverClassName: String,
        jdbcConnectionString: String?
    ): DataSource {
        return DataSourceBuilder(username, password, driverClassName, jdbcConnectionString).build()
    }

    /**
     * Constructs a new [DataSource] using the provided configuration.
     *
     * @param username The username of the database user.
     * @param password The password of the database user.
     * @param driverClassName The fully qualified name of the JDBC driver class.
     * @param jdbcConnectionString The JDBC connection string.
     * @param connectionProperties Additional configuration properties for the underlying driver.
     * @return The configured [DataSource].
     */
    @JvmStatic
    fun create(
        username: String?,
        password: String?,
        driverClassName: String,
        jdbcConnectionString: String?,
        connectionProperties: Map<String, String>?,
        connectionTimeout: Duration?
    ): DataSource {
        return DataSourceBuilder(username, password, driverClassName, jdbcConnectionString)
            .withConnectionProperties(connectionProperties)
            .withConnectionTimeout(connectionTimeout)
            .build()
    }

    /**
     * Constructs a new [DataSource] using the provided configuration.
     *
     * @param username The username of the database user.
     * @param password The password of the database user.
     * @param host The host address of the database.
     * @param port The port of the database.
     * @param database The name of the database.
     * @param driverClassName The fully qualified name of the JDBC driver class.
     * @return The configured [DataSource].
     */
    fun create(
        username: String?,
        password: String?,
        host: String?,
        port: Int,
        database: String?,
        driverClassName: String
    ): DataSource {
        return DataSourceBuilder(username, password, driverClassName, host, port, database).build()
    }

    /**
     * Constructs a new [DataSource] using the provided configuration.
     *
     * @param username The username of the database user.
     * @param password The password of the database user.
     * @param host The host address of the database.
     * @param port The port of the database.
     * @param database The name of the database.
     * @param driverClassName The fully qualified name of the JDBC driver class.
     * @param connectionProperties Additional configuration properties for the underlying driver.
     * @return The configured [DataSource].
     */
    fun create(
        username: String?,
        password: String?,
        host: String?,
        port: Int,
        database: String?,
        driverClassName: String,
        connectionProperties: Map<String, String>?
    ): DataSource {
        return DataSourceBuilder(username, password, driverClassName, host, port, database)
            .withConnectionProperties(connectionProperties)
            .build()
    }

    /**
     * Convenience method that constructs a new [DataSource] for a PostgreSQL database using the
     * provided configuration.
     *
     * @param username The username of the database user.
     * @param password The password of the database user.
     * @param host The host address of the database.
     * @param port The port of the database.
     * @param database The name of the database.
     * @return The configured [DataSource].
     */
    fun createPostgres(
        username: String?,
        password: String?,
        host: String?,
        port: Int,
        database: String?
    ): DataSource {
        return DataSourceBuilder(username, password, "org.postgresql.Driver", host, port, database)
            .build()
    }

    /**
     * Utility method that attempts to close the provided [DataSource] if it implements [Closeable].
     *
     * @param dataSource The [DataSource] to close.
     * @throws Exception if unable to close the data source.
     */
    @JvmStatic
    @Throws(Exception::class)
    fun close(dataSource: DataSource?) {
        if (dataSource != null) {
            if (dataSource is AutoCloseable) {
                dataSource.close()
            }
        }
    }

    /** Builder class used to configure and construct [DataSource] instances. */
    class DataSourceBuilder
    private constructor(
        private var username: String?,
        private var password: String?,
        private var driverClassName: String
    ) {
        private var connectionProperties: Map<String, String> = java.util.Map.of()
        private var database: String? = null
        private var host: String? = null
        private var jdbcUrl: String? = null
        private var maximumPoolSize = 10
        private var minimumPoolSize = 0
        private var connectionTimeout: Duration = Duration.ZERO
        private var port = 5432
        private var connectionInitSql: String? = null

        constructor(
            username: String?,
            password: String?,
            driverClassName: String,
            jdbcUrl: String?
        ) : this(username, password, driverClassName) {
            this.jdbcUrl = jdbcUrl
        }

        constructor(
            username: String?,
            password: String?,
            driverClassName: String,
            host: String?,
            port: Int,
            database: String?
        ) : this(username, password, driverClassName) {
            this.host = host
            this.port = port
            this.database = database
        }

        fun withConnectionProperties(
            connectionProperties: Map<String, String>?
        ): DataSourceBuilder {
            if (connectionProperties != null) {
                this.connectionProperties = connectionProperties
            }
            return this
        }

        fun withDatabase(database: String?): DataSourceBuilder {
            this.database = database
            return this
        }

        fun withDriverClassName(driverClassName: String): DataSourceBuilder {
            this.driverClassName = driverClassName
            return this
        }

        fun withHost(host: String?): DataSourceBuilder {
            this.host = host
            return this
        }

        fun withJdbcUrl(jdbcUrl: String?): DataSourceBuilder {
            this.jdbcUrl = jdbcUrl
            return this
        }

        fun withMaximumPoolSize(maximumPoolSize: Int): DataSourceBuilder {
            this.maximumPoolSize = maximumPoolSize
            return this
        }

        fun withMinimumPoolSize(minimumPoolSize: Int): DataSourceBuilder {
            this.minimumPoolSize = minimumPoolSize
            return this
        }

        fun withConnectionTimeout(connectionTimeout: Duration?): DataSourceBuilder {
            if (connectionTimeout != null) {
                this.connectionTimeout = connectionTimeout
            }
            return this
        }

        fun withPassword(password: String?): DataSourceBuilder {
            this.password = password
            return this
        }

        fun withPort(port: Int): DataSourceBuilder {
            this.port = port
            return this
        }

        fun withUsername(username: String?): DataSourceBuilder {
            this.username = username
            return this
        }

        fun withConnectionInitSql(sql: String?): DataSourceBuilder {
            this.connectionInitSql = sql
            return this
        }

        fun build(): DataSource {
            val databaseDriver: DatabaseDriver =
                DatabaseDriver.Companion.findByDriverClassName(driverClassName)

            Preconditions.checkNotNull(
                databaseDriver,
                "Unknown or blank driver class name: '$driverClassName'."
            )

            val config = HikariConfig()

            config.driverClassName = databaseDriver.driverClassName
            config.jdbcUrl =
                if (jdbcUrl != null) jdbcUrl
                else String.format(databaseDriver.urlFormatString, host, port, database)
            config.maximumPoolSize = maximumPoolSize
            config.minimumIdle = minimumPoolSize
            // HikariCP uses milliseconds for all time values:
            // https://github.com/brettwooldridge/HikariCP#gear-configuration-knobs-baby
            config.connectionTimeout = connectionTimeout.toMillis()
            config.password = password
            config.username = username

            /*
             * Disable to prevent failing on startup. Applications may start prior to the database container
             * being available. To avoid failing to create the connection pool, disable the fail check. This
             * will preserve existing behavior that tests for the connection on first use, not on creation.
             */
            config.initializationFailTimeout = Int.MIN_VALUE.toLong()

            config.connectionInitSql = connectionInitSql

            connectionProperties.forEach { (propertyName: String?, value: String?) ->
                config.addDataSourceProperty(propertyName, value)
            }

            return HikariDataSource(config)
        }
    }
}
