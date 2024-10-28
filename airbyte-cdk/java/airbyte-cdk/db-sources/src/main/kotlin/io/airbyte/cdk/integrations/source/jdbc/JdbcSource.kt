/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.Source
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.JDBCType
import java.util.function.Supplier

private val LOGGER = KotlinLogging.logger {}

class JdbcSource :
    AbstractJdbcSource<JDBCType>(
        DatabaseDriver.POSTGRESQL.driverClassName,
        Supplier { AdaptiveStreamingQueryConfig() },
        JdbcUtils.defaultSourceOperations
    ),
    Source {
    // no-op for JdbcSource since the config it receives is designed to be use for JDBC.
    override fun toDatabaseConfig(config: JsonNode): JsonNode {
        return config
    }

    override val excludedInternalNameSpaces: Set<String>
        get() = setOf("information_schema", "pg_catalog", "pg_internal", "catalog_history")

    companion object {

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            val source: Source = JdbcSource()
            LOGGER.info { "starting source: ${JdbcSource::class.java}" }
            IntegrationRunner(source).run(args)
            LOGGER.info { "completed source: ${JdbcSource::class.java}" }
        }
    }
}
