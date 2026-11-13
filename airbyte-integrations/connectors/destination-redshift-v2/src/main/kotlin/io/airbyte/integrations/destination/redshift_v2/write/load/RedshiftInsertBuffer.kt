/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.PreparedStatement
import java.sql.Timestamp
import java.sql.Types
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

/**
 * Accumulates records and flushes to Redshift in batches. NOT a @Singleton - created per-stream by
 * AggregateFactory.
 */
class RedshiftInsertBuffer(
    private val tableName: TableName,
    private val dataSource: DataSource,
    private val flushLimit: Int = 1000,
) {
    private val buffer = mutableListOf<Map<String, AirbyteValue>>()
    private var recordCount = 0

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        buffer.add(recordFields)
        recordCount++

        if (recordCount >= flushLimit) {
            kotlinx.coroutines.runBlocking { flush() }
        }
    }

    suspend fun flush() {
        if (buffer.isEmpty()) return

        try {
            log.info { "Flushing $recordCount records to $tableName..." }

            dataSource.connection.use { _ -> buffer.forEach { record -> insertRecord(record) } }

            log.info { "Finished flushing $recordCount records" }
        } finally {
            buffer.clear()
            recordCount = 0
        }
    }

    private fun insertRecord(record: Map<String, AirbyteValue>) {
        val columns = record.keys.joinToString(", ") { "\"$it\"" }
        val placeholders = record.keys.joinToString(", ") { "?" }
        val sql =
            """
            INSERT INTO "${tableName.namespace}"."${tableName.name}" ($columns)
            VALUES ($placeholders)
        """.trimIndent()

        dataSource.connection.use { connection ->
            connection.prepareStatement(sql).use { statement ->
                record.values.forEachIndexed { index, value ->
                    setParameter(statement, index + 1, value)
                }
                statement.executeUpdate()
            }
        }
    }

    private fun setParameter(statement: PreparedStatement, index: Int, value: AirbyteValue) {
        when (value) {
            is NullValue -> statement.setNull(index, Types.VARCHAR)
            is StringValue -> statement.setString(index, value.value.replace("\u0000", " "))
            is IntegerValue -> statement.setLong(index, value.value.toLong())
            is NumberValue -> statement.setDouble(index, value.value.toDouble())
            is BooleanValue -> statement.setBoolean(index, value.value)
            is DateValue -> {
                statement.setDate(index, java.sql.Date.valueOf(value.value))
            }
            is TimeWithTimezoneValue -> {
                // Redshift TIME type - convert to string
                statement.setString(index, value.value.toString())
            }
            is TimeWithoutTimezoneValue -> {
                // Redshift TIME type - convert to string
                statement.setString(index, value.value.toString())
            }
            is TimestampWithTimezoneValue -> {
                // Convert OffsetDateTime to Timestamp
                statement.setTimestamp(index, Timestamp.from(value.value.toInstant()))
            }
            is TimestampWithoutTimezoneValue -> {
                // Convert LocalDateTime to Timestamp
                statement.setTimestamp(index, Timestamp.valueOf(value.value))
            }
            is ObjectValue -> {
                // Redshift SUPER type accepts JSON strings
                statement.setString(index, value.values.serializeToString())
            }
            is ArrayValue -> {
                // Redshift SUPER type accepts JSON strings
                statement.setString(index, value.values.serializeToString())
            }
        }
    }
}
