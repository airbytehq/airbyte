/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.DefaultImplementation
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet

@DefaultImplementation(JdbcSelectQuerier::class)
interface SelectQuerier {
    fun executeQuery(
        q: SelectQuery,
        parameters: Parameters = Parameters(),
    ): Result

    data class Parameters(
        /** When set, the [ObjectNode] in the [Result] is reused; take care with this! */
        val reuseResultObject: Boolean = false,
        /** JDBC fetchSize value. */
        val fetchSize: Int? = null,
    )

    interface Result : Iterator<ObjectNode>, AutoCloseable
}

/** Default implementation of [SelectQuerier]. */
@Singleton
class JdbcSelectQuerier(
    private val jdbcConnectionFactory: JdbcConnectionFactory,
) : SelectQuerier {
    override fun executeQuery(
        q: SelectQuery,
        parameters: SelectQuerier.Parameters,
    ): SelectQuerier.Result = Result(q, parameters)

    private inner class Result(
        val q: SelectQuery,
        parameters: SelectQuerier.Parameters,
    ) : SelectQuerier.Result {
        private val log = KotlinLogging.logger {}

        var conn: Connection? = null
        var stmt: PreparedStatement? = null
        var rs: ResultSet? = null
        val reusable: ObjectNode? = Jsons.objectNode().takeIf { parameters.reuseResultObject }

        init {
            log.info { "Querying ${q.sql}" }
            try {
                conn = jdbcConnectionFactory.get()
                stmt = conn!!.prepareStatement(q.sql)
                parameters.fetchSize?.let { fetchSize: Int ->
                    log.info { "Setting fetchSize to $fetchSize." }
                    stmt!!.fetchSize = fetchSize
                }
                var paramIdx = 1
                for (binding in q.bindings) {
                    log.info { "Setting parameter #$paramIdx to $binding." }
                    binding.type.set(stmt!!, paramIdx, binding.value)
                    paramIdx++
                }
                rs = stmt!!.executeQuery()
            } catch (e: Throwable) {
                close()
                throw e
            }
        }

        var isReady = false
        var hasNext = false
        var hasLoggedResultsReceived = false

        override fun hasNext(): Boolean {
            // hasNext() is idempotent
            if (isReady) return hasNext
            // Advance to the next row to become ready again.
            hasNext = rs!!.next()
            if (!hasLoggedResultsReceived) {
                log.info { "Received results from server." }
                hasLoggedResultsReceived = true
            }
            if (!hasNext) {
                close()
            }
            isReady = true
            return hasNext
        }

        override fun next(): ObjectNode {
            // Ensure that the current row in the ResultSet hasn't been read yet; advance if
            // necessary.
            if (!hasNext()) throw NoSuchElementException()
            // Read the current row in the ResultSet
            val record: ObjectNode = reusable ?: Jsons.objectNode()
            var colIdx = 1
            for (column in q.columns) {
                log.debug { "Getting value #$colIdx for $column." }
                val jdbcFieldType: JdbcFieldType<*> = column.type as JdbcFieldType<*>
                record.set<JsonNode>(column.id, jdbcFieldType.get(rs!!, colIdx))
                colIdx++
            }
            // Flag that the current row has been read before returning.
            isReady = false
            return record
        }

        override fun close() {
            // close() is idempotent
            isReady = true
            hasNext = false
            try {
                if (rs != null) {
                    log.info { "Closing ${q.sql}" }
                    rs!!.close()
                }
            } finally {
                rs = null
                try {
                    stmt?.close()
                } finally {
                    stmt = null
                    try {
                        conn?.close()
                    } finally {
                        conn = null
                    }
                }
            }
        }
    }
}
