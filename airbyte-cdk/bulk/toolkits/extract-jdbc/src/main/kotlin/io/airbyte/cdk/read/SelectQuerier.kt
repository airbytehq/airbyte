/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcFieldType
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
//        val data: ObjectNode
        val data: InternalRow
        val changes: Map<Field, FieldValueChange>
    }
}

data class FieldValueEncoder(val value: Any?, val jsonEncoder: JsonEncoder<Any>)
typealias InternalRow = MutableMap<String, FieldValueEncoder>


fun InternalRow.toJson(parentNode: ObjectNode): ObjectNode {
    for ((columnId, value) in this) {
        val encodedValue = value.jsonEncoder.encode(value.value!!)
        parentNode.set<JsonNode>(columnId, encodedValue ?: NullNode.instance)
    }
    return parentNode
}

/*
fun InternalRow.toProto(): AirbyteRecordMessage.AirbyteRecordMessageProtobuf =
    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
        .apply {
            for ((columnId, value) in this@toProto) {
                addData(AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setInteger(value.value as Long)) // Adjust based on actual type
            }
        }
        .build()
*/
/** Default implementation of [SelectQuerier]. */
@Singleton
class JdbcSelectQuerier(
    private val jdbcConnectionFactory: JdbcConnectionFactory,
) : SelectQuerier {
    override fun executeQuery(
        q: SelectQuery,
        parameters: SelectQuerier.Parameters,
    ): SelectQuerier.Result = Result(jdbcConnectionFactory, q, parameters)

    data class ResultRow(
//        override var data: ObjectNode = Jsons.objectNode(),
        override val data: InternalRow = mutableMapOf(),
        override var changes: MutableMap<Field, FieldValueChange> = mutableMapOf(),
    ) : SelectQuerier.ResultRow

    class Result(
        val jdbcConnectionFactory: JdbcConnectionFactory,
        val q: SelectQuery,
        val parameters: SelectQuerier.Parameters,
    ) : SelectQuerier.Result {
        private val log = KotlinLogging.logger {}

        var conn: Connection? = null
        var stmt: PreparedStatement? = null
        var rs: ResultSet? = null
        val reusable: ResultRow? = ResultRow().takeIf { parameters.reuseResultObject }

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
        fun initQueryExecution() {
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
            val resultRow: ResultRow = reusable ?: ResultRow()
            resultRow.changes.clear()
            var colIdx = 1

//            val interMap: InternalRow = mutableMapOf()
            for (column in q.columns) {
                log.debug { "Getting value #$colIdx for $column." }
                val jdbcFieldType: JdbcFieldType<*> = column.type as JdbcFieldType<*>
                try {

/*
                    interMap[column.id] = FieldValueEncoder(
                        jdbcFieldType.jdbcGetter.get(rs!!, colIdx),
                        jdbcFieldType.jsonEncoder as JsonEncoder<Any>
                    )
*/
                    resultRow.data[column.id] = FieldValueEncoder(
                        jdbcFieldType.jdbcGetter.get(rs!!, colIdx),
                        jdbcFieldType.jsonEncoder as JsonEncoder<Any>
                    )

/*
                    when (interMap[column.id]) {
                        is Long -> {
                            val l: Long = interMap[column.id] as Long
                            val f = LongFieldType as JdbcFieldType<Long>
                            resultRow.data.set<JsonNode>(column.id, f.jsonEncoder.encode(l))
                        }
                    }
*/
//                    resultRow.data.set<JsonNode>(column.id, jdbcFieldType.get(rs!!, colIdx))
                } catch (e: Exception) {
                    resultRow.data[column.id] = FieldValueEncoder(
                        null,
                        NullCodec as JsonEncoder<Any> // Use NullCodec for null values
                    ) // Use NullCodec for null values
//                    resultRow.data.set<JsonNode>(column.id, Jsons.nullNode())
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

//            interMap.toJson(resultRow.data)


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
