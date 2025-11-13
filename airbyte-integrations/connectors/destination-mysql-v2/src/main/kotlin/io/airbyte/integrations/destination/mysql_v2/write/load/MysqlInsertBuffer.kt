package io.airbyte.integrations.destination.mysql_v2.write.load

import io.airbyte.cdk.load.data.AirbyteValue
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
import io.airbyte.integrations.destination.mysql_v2.client.MysqlAirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.runBlocking
import java.sql.PreparedStatement
import java.sql.Timestamp
import java.sql.Types

private val log = KotlinLogging.logger {}

/**
 * Buffers records and performs batch inserts to MySQL.
 *
 * Strategy: Use multi-row INSERT statements with prepared statements and batch execution.
 * This provides good performance without requiring special permissions (LOAD DATA INFILE).
 *
 * Example: INSERT INTO table (col1, col2) VALUES (?, ?), (?, ?), (?, ?)
 */
class MysqlInsertBuffer(
    private val tableName: TableName,
    private val columns: List<String>,
    private val mysqlClient: MysqlAirbyteClient,
    private val flushLimit: Int = 5000,
) {
    private val recordBatch = mutableListOf<Map<String, AirbyteValue>>()
    private var recordCount = 0

    /**
     * Accumulates a record. Auto-flushes when batch size reaches the limit.
     */
    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        recordBatch.add(recordFields)
        recordCount++

        if (recordCount >= flushLimit) {
            runBlocking { flush() }
        }
    }

    /**
     * Flushes all accumulated records to the database using batch INSERT.
     */
    suspend fun flush() {
        if (recordBatch.isEmpty()) {
            log.debug { "Buffer is empty, skipping flush for ${tableName.name}" }
            return
        }

        try {
            log.info { "Flushing $recordCount records to ${tableName.namespace}.${tableName.name}..." }

            val startTime = System.currentTimeMillis()

            // Use batch INSERT for better performance
            mysqlClient.executeBatchInsert(tableName, columns, recordBatch)

            val duration = System.currentTimeMillis() - startTime
            log.info {
                "Successfully flushed $recordCount records to ${tableName.name} in ${duration}ms " +
                "(${recordCount * 1000 / maxOf(duration, 1)} records/sec)"
            }
        } catch (e: Exception) {
            log.error(e) { "Failed to flush $recordCount records to ${tableName.name}" }
            throw e
        } finally {
            recordBatch.clear()
            recordCount = 0
        }
    }
}

/**
 * Executes a batch INSERT statement.
 * Adds this method to MysqlAirbyteClient via extension for better separation of concerns.
 */
suspend fun MysqlAirbyteClient.executeBatchInsert(
    tableName: TableName,
    columns: List<String>,
    records: List<Map<String, AirbyteValue>>
) {
    if (records.isEmpty()) return

    // Build INSERT statement with placeholders
    val columnList = columns.joinToString(", ") { "`$it`" }
    val placeholders = columns.joinToString(", ") { "?" }

    // For very large batches, split into chunks to avoid MySQL packet size limits
    val chunkSize = 1000
    val chunks = records.chunked(chunkSize)

    chunks.forEach { chunk ->
        val valuesClause = chunk.joinToString(", ") { "($placeholders)" }

        val sql = """
            INSERT INTO `${tableName.namespace}`.`${tableName.name}` ($columnList)
            VALUES $valuesClause
        """.trimIndent()

        executeWithPreparedStatement(sql) { stmt ->
            var paramIndex = 1
            chunk.forEach { record ->
                columns.forEach { col ->
                    setParameter(stmt, paramIndex++, record[col] ?: NullValue)
                }
            }
            stmt.executeUpdate()
        }
    }
}

/**
 * Sets a parameter in a PreparedStatement based on the AirbyteValue type.
 */
private fun setParameter(statement: PreparedStatement, index: Int, value: AirbyteValue) {
    when (value) {
        is StringValue -> statement.setString(index, value.value)
        is IntegerValue -> statement.setLong(index, value.value.toLong())
        is NumberValue -> statement.setBigDecimal(index, value.value)
        is BooleanValue -> statement.setBoolean(index, value.value)
        is TimestampWithTimezoneValue -> statement.setTimestamp(index, Timestamp.from(value.value.toInstant()))
        is TimestampWithoutTimezoneValue -> statement.setTimestamp(index, Timestamp.valueOf(value.value))
        is TimeWithTimezoneValue -> statement.setTime(index, java.sql.Time.valueOf(value.value.toLocalTime()))
        is TimeWithoutTimezoneValue -> statement.setTime(index, java.sql.Time.valueOf(value.value))
        is DateValue -> statement.setDate(index, java.sql.Date.valueOf(value.value))
        is ObjectValue, is io.airbyte.cdk.load.data.ArrayValue -> {
            // Store JSON as string
            statement.setString(index, value.toString())
        }
        is NullValue -> statement.setNull(index, Types.VARCHAR)
        else -> {
            // Fallback: convert to string
            log.warn { "Unknown AirbyteValue type: ${value::class.simpleName}, converting to string" }
            statement.setString(index, value.toString())
        }
    }
}

/**
 * Extension function to execute SQL with a prepared statement.
 * Adds this to MysqlAirbyteClient for reusability.
 */
private suspend fun MysqlAirbyteClient.executeWithPreparedStatement(
    sql: String,
    block: (PreparedStatement) -> Unit
) {
    dataSource.connection.use { connection ->
        connection.prepareStatement(sql).use { statement ->
            block(statement)
        }
    }
}
