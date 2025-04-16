/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.output.SocketConfig
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.AirbyteRecord
import io.airbyte.protocol.AirbyteRecord.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.DefaultImplementation
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime

@DefaultImplementation(JdbcSelectQuerier::class)
interface SelectQuerier {
    fun executeQuery(
        q: SelectQuery,
        parameters: Parameters = Parameters(),
        cursorQuery: Boolean = false
    ): Result

    data class Parameters(
        /** When set, the [ObjectNode] in the [Result] is reused; take care with this! */
        val reuseResultObject: Boolean,
        /** JDBC [PreparedStatement] fetchSize value. */
        val statementFetchSize: Int?,
        /** JDBC [ResultSet] fetchSize value. */
        val resultSetFetchSize: Int?,
    ) {
        constructor(
            reuseResultObject: Boolean = false,
            fetchSize: Int? = null
        ) : this(reuseResultObject, fetchSize, fetchSize)
    }

    interface Result : Iterator<ResultRow>, AutoCloseable

    interface ResultRow {
        val data: ObjectNode
        val changes: Map<Field, FieldValueChange>
        val recordBuilder: AirbyteRecordMessage.Builder get() = AirbyteRecordMessage.newBuilder()
    }
}

val dummyCell: AirbyteRecord.AirbyteValue = AirbyteRecord.AirbyteValue.newBuilder().setBoolean(false).build()

/** Default implementation of [SelectQuerier]. */
@Singleton
class JdbcSelectQuerier(
    private val jdbcConnectionFactory: JdbcConnectionFactory,
    private val socketConfig: SocketConfig,
) : SelectQuerier {
    override fun executeQuery(
        q: SelectQuery,
        parameters: SelectQuerier.Parameters,
        cursorQuery: Boolean
    ): SelectQuerier.Result =
        Result(
            jdbcConnectionFactory,
            q,
            parameters,
            writeProto = socketConfig.skipJsonNodeAndUseFakeRecord
        )

    data class ResultRow(
        override var data: ObjectNode = Jsons.objectNode(),
        override var changes: MutableMap<Field, FieldValueChange> = mutableMapOf(),
        override val recordBuilder: AirbyteRecordMessage.Builder = AirbyteRecordMessage.newBuilder().also { repeat(17) { _ -> it.addData(dummyCell) } },
        val valueBuilder: AirbyteRecord.AirbyteValue.Builder = AirbyteRecord.AirbyteValue.newBuilder()
    ) : SelectQuerier.ResultRow

    open class Result(
        val jdbcConnectionFactory: JdbcConnectionFactory,
        val q: SelectQuery,
        val parameters: SelectQuerier.Parameters,
        val writeProto: Boolean = false,
    ) : SelectQuerier.Result {
        private val log = KotlinLogging.logger {}

        var conn: Connection? = null
        var stmt: PreparedStatement? = null
        var rs: ResultSet? = null
        val reusable: ResultRow = ResultRow()

        init {
            log.info { "Querying ${q.sql}" }
            try {
                initQueryExecution()
            } catch (e: Throwable) {
                close()
                throw e
            }
        }

        var isReady = false
        var hasNext = false
        var hasLoggedResultsReceived = false
        var hasLoggedException = false

        /** Initializes a connection and readies the resultset. */
        open fun initQueryExecution() {
            conn = jdbcConnectionFactory.get()
            stmt = conn!!.prepareStatement(q.sql)
            parameters.statementFetchSize?.let { fetchSize: Int ->
                log.info { "Setting Statement fetchSize to $fetchSize." }
                stmt!!.fetchSize = fetchSize
            }
            var paramIdx = 1
            for (binding in q.bindings) {
                log.info { "Setting parameter #$paramIdx to $binding." }
                binding.type.set(stmt!!, paramIdx, binding.value)
                paramIdx++
            }
            rs = stmt!!.executeQuery()
            parameters.resultSetFetchSize?.let { fetchSize: Int ->
                log.info { "Setting ResultSet fetchSize to $fetchSize." }
                rs!!.fetchSize = fetchSize
            }
        }

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

        override fun next(): SelectQuerier.ResultRow {
            // Ensure that the current row in the ResultSet hasn't been read yet; advance if
            // necessary.
            if (!hasNext()) throw NoSuchElementException()
            // Read the current row in the ResultSet
            val resultRow: ResultRow = reusable
            resultRow.changes.clear()
            var colIdx = 1
            for (column in q.columns) {
                log.debug { "Getting value #$colIdx for $column." }
                val jdbcFieldType: JdbcFieldType<*> = column.type as JdbcFieldType<*>
                try {
                    if (!writeProto) {
                        resultRow.data.set<JsonNode>(column.id, jdbcFieldType.get(rs!!, colIdx))
                    } else {
                        // Fetch and discard the data w/o marshaling to JSON
                        when (val value = jdbcFieldType.getValueOnly(rs!!, colIdx)) {
                            is String -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(value))
                            }
                            is Int -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setInteger(value.toLong()))
                            }
                            is Long -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setInteger(value))
                            }
                            is BigDecimal -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setNumber(value.toDouble()))
                            }
                            is Double -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setNumber(value))
                            }
                            is Float -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setNumber(value.toDouble()))
                            }
                            is Boolean -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setBoolean(value))
                            }
                            is LocalDateTime -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(value.toString()))
                            }
                            is LocalTime -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(value.toString()))
                            }
                            is LocalDate -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(value.toString()))
                            }
                            null -> {
                                // TODO: Set is_null
                            }
                            else -> {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(value.toString()))
                            }
                        }
                    }
                } catch (e: Exception) {
                    resultRow.data.set<JsonNode>(column.id, Jsons.nullNode())
                    if (!hasLoggedException) {
                        log.warn(e) { "Error deserializing value in column $column." }
                        hasLoggedException = true
                    } else {
                        log.debug(e) { "Error deserializing value in column $column." }
                    }
                    resultRow.changes.set(column, FieldValueChange.RETRIEVAL_FAILURE_TOTAL)
                }
                colIdx++
            }
            // Flag that the current row has been read before returning.
            isReady = false
            return resultRow
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
