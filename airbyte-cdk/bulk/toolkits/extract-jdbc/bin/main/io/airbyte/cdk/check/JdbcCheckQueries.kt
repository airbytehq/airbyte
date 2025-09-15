/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.check

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement

const val CHECK_QUERIES_PREFIX = "airbyte.connector.check.jdbc"

/**
 * Micronaut configuration object which implements
 * [io.airbyte.cdk.discover.MetadataQuerier.extraChecks] in
 * [io.airbyte.cdk.discover.JdbcMetadataQuerier].
 *
 * The configuration values are a list of SQL queries which are executed in sequence. Any query
 * which returns a non-empty result set containing anything other than NULL values or blank strings
 * will throw a [io.airbyte.cdk.ConfigErrorException].
 */
@Singleton
@ConfigurationProperties(CHECK_QUERIES_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class JdbcCheckQueries {

    // Micronaut configuration objects work better with mutable properties.
    protected var queries: List<String> = emptyList()

    private val log = KotlinLogging.logger {}

    /** Delegated to by [io.airbyte.cdk.discover.JdbcMetadataQuerier.extraChecks]. */
    fun executeAll(conn: Connection) {
        if (queries.isEmpty()) return
        log.info { "Executing ${queries.size} check queries." }
        queries.forEachIndexed { index: Int, sql: String ->
            conn.createStatement().use { stmt: Statement ->
                log.info { "Executing check query ${index+1} / ${queries.size}: '$sql'." }
                val error: String = stmt.executeQuery(sql).use { rs: ResultSet -> stringify(rs) }
                if (error.isNotBlank()) {
                    log.warn { "Check query ${index+1} / ${queries.size} failed with: '$error'." }
                    throw ConfigErrorException(error)
                }
                log.info { "Check query ${index+1} / ${queries.size} succeeded." }
            }
        }
    }

    companion object {

        /** Turns a [ResultSet] into a pretty and meaningful one-line string; empty otherwise. */
        fun stringify(rs: ResultSet): String {
            val sb = StringBuilder()
            var firstRow = true
            while (rs.next()) {
                var firstColumn = true
                for (i in 1..rs.metaData.columnCount) {
                    // Get column value, ignore NULLs or blank strings
                    val value: String =
                        rs.getString(i)?.takeUnless { rs.wasNull() }?.takeUnless { it.isBlank() }
                            ?: continue
                    // Print column or row separator, if required
                    if (firstColumn) {
                        firstColumn = false
                        if (firstRow) {
                            firstRow = false
                        } else {
                            sb.append("; ")
                        }
                    } else {
                        sb.append(", ")
                    }
                    // Print key-value pair
                    sb.append(rs.metaData.getColumnName(i)).append(": ").append(value)
                }
            }
            return sb.toString().trim()
        }
    }
}
