/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import java.time.Duration
import java.time.temporal.ChronoUnit
import java.time.temporal.TemporalUnit
import java.util.*

abstract class JdbcConnector
protected constructor(@JvmField protected val driverClassName: String) : BaseConnector() {
    protected fun getConnectionTimeout(connectionProperties: Map<String, String>): Duration {
        return getConnectionTimeout(connectionProperties, driverClassName)
    }

    companion object {
        const val POSTGRES_CONNECT_TIMEOUT_KEY: String = "connectTimeout"
        val POSTGRES_CONNECT_TIMEOUT_DEFAULT_DURATION: Duration = Duration.ofSeconds(10)

        const val CONNECT_TIMEOUT_KEY: String = "connectTimeout"
        @JvmField val CONNECT_TIMEOUT_DEFAULT: Duration = Duration.ofSeconds(60)

        /**
         * Retrieves connectionTimeout value from connection properties in millis, default minimum
         * timeout is 60 seconds since Hikari default of 30 seconds is not enough for acceptance
         * tests. In the case the value is 0, pass the value along as Hikari and Postgres use
         * default max value for 0 timeout value.
         *
         * NOTE: Postgres timeout is measured in seconds:
         * https://jdbc.postgresql.org/documentation/head/connect.html
         *
         * @param connectionProperties custom jdbc_url_parameters containing information on
         * connection properties
         * @param driverClassName name of the JDBC driver
         * @return DataSourceBuilder class used to create dynamic fields for DataSource
         */
        @JvmStatic
        fun getConnectionTimeout(
            connectionProperties: Map<String, String>,
            driverClassName: String?
        ): Duration {
            val parsedConnectionTimeout =
                when (DatabaseDriver.Companion.findByDriverClassName(driverClassName)) {
                    DatabaseDriver.POSTGRESQL ->
                        maybeParseDuration(
                                connectionProperties[POSTGRES_CONNECT_TIMEOUT_KEY],
                                ChronoUnit.SECONDS
                            )
                            .or { Optional.of<Duration>(POSTGRES_CONNECT_TIMEOUT_DEFAULT_DURATION) }
                    DatabaseDriver.MYSQL,
                    DatabaseDriver.SINGLESTORE ->
                        maybeParseDuration(
                            connectionProperties["connectTimeout"],
                            ChronoUnit.MILLIS
                        )
                    DatabaseDriver.MSSQLSERVER ->
                        maybeParseDuration(connectionProperties["loginTimeout"], ChronoUnit.SECONDS)
                    else ->
                        maybeParseDuration(
                                connectionProperties[CONNECT_TIMEOUT_KEY],
                                ChronoUnit.SECONDS
                            ) // Enforce minimum timeout duration for unspecified data sources.
                            .filter { d: Duration -> d.compareTo(CONNECT_TIMEOUT_DEFAULT) >= 0 }
                }
            return parsedConnectionTimeout.orElse(CONNECT_TIMEOUT_DEFAULT)
        }

        private fun maybeParseDuration(
            stringValue: String?,
            unit: TemporalUnit
        ): Optional<Duration> {
            if (stringValue == null) {
                return Optional.empty()
            }
            val number: Long
            try {
                number = stringValue.toLong()
            } catch (`__`: NumberFormatException) {
                return Optional.empty()
            }
            if (number < 0) {
                return Optional.empty()
            }
            return Optional.of(Duration.of(number, unit))
        }
    }
}
