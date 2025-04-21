/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.protobuf.ByteString
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.output.FlatBufferResult
import io.airbyte.cdk.output.SocketConfig
import io.airbyte.cdk.output.SocketOutputFormat
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.AirbyteBooleanValue
import io.airbyte.protocol.AirbyteLongValue
import io.airbyte.protocol.AirbyteNumberValue
import io.airbyte.protocol.AirbyteRecord
import io.airbyte.protocol.AirbyteRecord.AirbyteRecordMessage
import io.airbyte.protocol.AirbyteStringValue
import io.airbyte.protocol.AirbyteValue
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.DefaultImplementation
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet

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
        val fbr: FlatBufferResult get() = FlatBufferResult()
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
            if (cursorQuery) { SocketOutputFormat.JSONL } else { socketConfig.outputFormat }
        )

    data class ResultRow(
        override var data: ObjectNode = Jsons.objectNode(),
        override var changes: MutableMap<Field, FieldValueChange> = mutableMapOf(),
        override val recordBuilder: AirbyteRecordMessage.Builder = AirbyteRecordMessage.newBuilder().also { repeat(17) { _ -> it.addData(dummyCell) } },
        val valueBuilder: AirbyteRecord.AirbyteValue.Builder = AirbyteRecord.AirbyteValue.newBuilder(),
        val fbTypeData: ByteArray = ByteArray(17) { 0.toByte() },
        val fbData: IntArray = IntArray(17) { 0 },
        override val fbr: FlatBufferResult = FlatBufferResult(),
    ) : SelectQuerier.ResultRow

    open class Result(
        val jdbcConnectionFactory: JdbcConnectionFactory,
        val q: SelectQuery,
        val parameters: SelectQuerier.Parameters,
        var outputFormat: SocketOutputFormat
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
            val resultRow = reusable
            resultRow.changes.clear()
            var colIdx = 1
            for (column in q.columns) {
                log.debug { "Getting value #$colIdx for $column." }
                val jdbcFieldType: JdbcFieldType<*> = column.type as JdbcFieldType<*>
                try {
                    when (outputFormat) {
                        SocketOutputFormat.PROTOBUF -> {
                            when (column.type.airbyteSchemaType) {
                                is ArrayAirbyteSchemaType -> TODO()
                                LeafAirbyteSchemaType.BOOLEAN ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setBoolean(rs!!.getBoolean(colIdx)))
                                LeafAirbyteSchemaType.STRING ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(rs!!.getString(colIdx)))
                                LeafAirbyteSchemaType.BINARY ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setBinary(ByteString.copyFrom(rs!!.getBytes(colIdx))))
                                LeafAirbyteSchemaType.DATE ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(rs!!.getDate(colIdx).toString()))
                                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(rs!!.getTime(colIdx).toString()))
                                LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(rs!!.getTime(colIdx).toString()))
                                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> {
                                    val ts = rs!!.getTimestamp(colIdx)
                                    resultRow.recordBuilder.setData(
                                        colIdx - 1,
                                        resultRow.valueBuilder.setTimestamp(
                                            com.google.protobuf.Timestamp.newBuilder()
                                                .setSeconds(ts.time / 1000)
                                                .setNanos((ts.time % 1000 * 1_000_000).toInt())
                                        )
                                    )
                                }
                                LeafAirbyteSchemaType.INTEGER ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setInteger(rs!!.getLong(colIdx)))
                                LeafAirbyteSchemaType.NUMBER ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setNumber(rs!!.getDouble(colIdx)))
                                LeafAirbyteSchemaType.NULL ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setIsNull(true))
                                LeafAirbyteSchemaType.JSONB ->
                                    resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setString(rs!!.getString(colIdx)))
                            }
                            if (rs!!.wasNull()) {
                                resultRow.recordBuilder.setData(colIdx - 1, resultRow.valueBuilder.setIsNull(true))
                            }
                        }
                        SocketOutputFormat.FLATBUFFERS -> {
                            resultRow.fbData[colIdx - 1] = when (column.type.airbyteSchemaType) {
                                is ArrayAirbyteSchemaType -> TODO()
                                LeafAirbyteSchemaType.STRING -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteStringValue
                                    resultRow.fbr.fbBuilder.createString(rs!!.getString(colIdx))
                                        .let { offset ->
                                            AirbyteStringValue.createAirbyteStringValue(
                                                resultRow.fbr.fbBuilder,
                                                offset
                                            )
                                        }
                                }

                                LeafAirbyteSchemaType.BOOLEAN -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteBooleanValue
                                    AirbyteBooleanValue.createAirbyteBooleanValue(
                                        resultRow.fbr.fbBuilder,
                                        rs!!.getBoolean(colIdx)
                                    )
                                        .let { offset ->
                                            AirbyteStringValue.createAirbyteStringValue(
                                                resultRow.fbr.fbBuilder,
                                                offset
                                            )
                                        }
                                }

                                LeafAirbyteSchemaType.BINARY -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteStringValue
                                    resultRow.fbr.fbBuilder.createByteVector(rs!!.getBytes(colIdx))
                                        .let { offset ->
                                            AirbyteStringValue.createAirbyteStringValue(
                                                resultRow.fbr.fbBuilder,
                                                offset
                                            )
                                        }
                                }

                                LeafAirbyteSchemaType.DATE -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteStringValue
                                    resultRow.fbr.fbBuilder.createString(
                                        rs!!.getDate(colIdx).toString()
                                    )
                                        .let { offset ->
                                            AirbyteStringValue.createAirbyteStringValue(
                                                resultRow.fbr.fbBuilder,
                                                offset
                                            )
                                        }
                                }

                                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteStringValue
                                    resultRow.fbr.fbBuilder.createString(
                                        rs!!.getTime(colIdx).toString()
                                    )
                                        .let { offset ->
                                            AirbyteStringValue.createAirbyteStringValue(
                                                resultRow.fbr.fbBuilder,
                                                offset
                                            )
                                        }
                                }

                                LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteStringValue
                                    resultRow.fbr.fbBuilder.createString(
                                        rs!!.getTime(colIdx).toString()
                                    )
                                        .let { offset ->
                                            AirbyteStringValue.createAirbyteStringValue(
                                                resultRow.fbr.fbBuilder,
                                                offset
                                            )
                                        }
                                }

                                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteLongValue
                                    AirbyteLongValue.createAirbyteLongValue(
                                        resultRow.fbr.fbBuilder,
                                        rs!!.getTimestamp(colIdx).time
                                    )
                                }

                                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteLongValue
                                    AirbyteLongValue.createAirbyteLongValue(
                                        resultRow.fbr.fbBuilder,
                                        rs!!.getTimestamp(colIdx).time
                                    )
                                }

                                LeafAirbyteSchemaType.INTEGER -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteLongValue
                                    AirbyteLongValue.createAirbyteLongValue(
                                        resultRow.fbr.fbBuilder,
                                        rs!!.getLong(colIdx)
                                    )
                                }

                                LeafAirbyteSchemaType.NUMBER -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteNumberValue
                                    AirbyteNumberValue.createAirbyteNumberValue(
                                        resultRow.fbr.fbBuilder,
                                        rs!!.getDouble(colIdx)
                                    )
                                }

                                LeafAirbyteSchemaType.NULL -> {
                                    0
                                }

                                LeafAirbyteSchemaType.JSONB -> {
                                    resultRow.fbTypeData[colIdx - 1] =
                                        AirbyteValue.AirbyteStringValue
                                    resultRow.fbr.fbBuilder.createString(rs!!.getString(colIdx))
                                        .let { offset ->
                                            AirbyteStringValue.createAirbyteStringValue(
                                                resultRow.fbr.fbBuilder,
                                                offset
                                            )
                                        }
                                }
                            }
                            if (rs!!.wasNull()) {
                                resultRow.fbTypeData[colIdx - 1] = 0
                                resultRow.fbData[colIdx - 1] = 0
                            }
                        }
                        else -> resultRow.data.set<JsonNode>(column.id, jdbcFieldType.get(rs!!, colIdx))
                    }
                } catch (e: Exception) {
                    resultRow.data.set<JsonNode>(column.id, Jsons.nullNode())
                    resultRow.fbTypeData[colIdx - 1] = 0
                    resultRow.fbData[colIdx - 1] = 0
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
            if (outputFormat == SocketOutputFormat.FLATBUFFERS) {
                resultRow.fbr.fbDataTypeVector = io.airbyte.protocol.AirbyteRecordMessage.createDataTypeVector(resultRow.fbr.fbBuilder, resultRow.fbTypeData)
                resultRow.fbr.fbDataVector = io.airbyte.protocol.AirbyteRecordMessage.createDataVector(resultRow.fbr.fbBuilder, resultRow.fbData)
            }
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
