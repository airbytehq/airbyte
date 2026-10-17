/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.write.load

import com.google.common.annotations.VisibleForTesting
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
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Date
import java.sql.PreparedStatement
import java.sql.Time
import java.sql.Timestamp
import java.sql.Types
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

/**
 * MySQL-specific buffering and writing logic using JDBC batch inserts.
 */
class MySQLInsertBuffer(
    val tableName: TableName,
    private val dataSource: DataSource,
    private val batchSize: Int = DEFAULT_BATCH_SIZE,
) {
    @VisibleForTesting
    internal val buffer = mutableListOf<Map<String, AirbyteValue>>()

    @VisibleForTesting
    internal var columnNames: List<String>? = null

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (columnNames == null && recordFields.isNotEmpty()) {
            columnNames = recordFields.keys.toList()
        }
        buffer.add(recordFields)

        if (buffer.size >= batchSize) {
            flushSync()
        }
    }

    suspend fun flush() {
        flushSync()
    }

    private fun flushSync() {
        if (buffer.isEmpty()) {
            log.debug { "Buffer is empty, nothing to flush for ${tableName.name}" }
            return
        }

        val cols = columnNames ?: return
        log.info { "Beginning batch insert of ${buffer.size} rows into ${tableName.namespace}.${tableName.name}" }

        dataSource.connection.use { connection ->
            val columnList = cols.joinToString(", ") { "`$it`" }
            val placeholders = cols.joinToString(", ") { "?" }
            val sql = "INSERT INTO `${tableName.namespace}`.`${tableName.name}` ($columnList) VALUES ($placeholders)"

            connection.prepareStatement(sql).use { statement ->
                buffer.forEach { record ->
                    cols.forEachIndexed { index, columnName ->
                        val value = record[columnName] ?: NullValue
                        setParameter(statement, index + 1, value)
                    }
                    statement.addBatch()
                }

                val results = statement.executeBatch()
                val insertedCount = results.count { it >= 0 }
                log.info { "Finished batch insert of $insertedCount rows into ${tableName.name}" }
            }
        }

        buffer.clear()
    }

    private fun setParameter(statement: PreparedStatement, index: Int, value: AirbyteValue) {
        when (value) {
            is StringValue -> statement.setString(index, value.value)
            is IntegerValue -> statement.setLong(index, value.value.toLong())
            is NumberValue -> statement.setBigDecimal(index, value.value)
            is BooleanValue -> statement.setBoolean(index, value.value)
            is TimestampWithTimezoneValue -> statement.setTimestamp(index, Timestamp.from(value.value.toInstant()))
            is TimestampWithoutTimezoneValue -> statement.setTimestamp(index, Timestamp.valueOf(value.value))
            is DateValue -> statement.setDate(index, Date.valueOf(value.value))
            is TimeWithTimezoneValue -> statement.setTime(index, Time.valueOf(value.value.toLocalTime()))
            is TimeWithoutTimezoneValue -> statement.setTime(index, Time.valueOf(value.value))
            is ObjectValue -> statement.setString(index, Jsons.writeValueAsString(value.values))
            is ArrayValue -> statement.setString(index, Jsons.writeValueAsString(value.values))
            is NullValue -> statement.setNull(index, Types.VARCHAR)
        }
    }

    companion object {
        const val DEFAULT_BATCH_SIZE = 1000
    }
}
