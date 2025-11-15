package io.airbyte.integrations.destination.mysql.write.load

import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mysql.client.MySQLAirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Date
import java.sql.PreparedStatement
import java.sql.Timestamp
import java.sql.Types
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

class MySQLInsertBuffer(
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
            log.info { "Flushing $recordCount records to ${tableName}..." }

            // Simple single-row INSERT for now
            // (Can optimize later with batch INSERT or LOAD DATA INFILE)
            buffer.forEach { record ->
                insertRecord(tableName, record)
            }

            log.info { "Finished flushing $recordCount records" }
        } finally {
            buffer.clear()
            recordCount = 0
        }
    }

    private fun insertRecord(
        tableName: TableName,
        record: Map<String, AirbyteValue>
    ) {
        val columns = record.keys.joinToString(", ") { "`$it`" }
        val placeholders = record.keys.joinToString(", ") { "?" }
        val sql = """
            INSERT INTO `${tableName.namespace}`.`${tableName.name}` ($columns)
            VALUES ($placeholders)
        """

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
            is StringValue -> statement.setString(index, value.value)
            is IntegerValue -> statement.setLong(index, value.value.toLong())
            is NumberValue -> statement.setBigDecimal(index, value.value)
            is BooleanValue -> statement.setBoolean(index, value.value)
            is DateValue -> statement.setDate(index, Date.valueOf(value.value))
            is TimestampWithTimezoneValue -> statement.setTimestamp(index, Timestamp.from(value.value.toInstant()))
            is TimestampWithoutTimezoneValue -> statement.setTimestamp(index, Timestamp.valueOf(value.value))
            is TimeWithTimezoneValue -> statement.setString(index, value.value.toString())
            is TimeWithoutTimezoneValue -> statement.setString(index, value.value.toString())
            is ObjectValue -> statement.setString(index, io.airbyte.cdk.load.util.Jsons.writeValueAsString(value.values))
            is ArrayValue -> statement.setString(index, io.airbyte.cdk.load.util.Jsons.writeValueAsString(value.values))
            is NullValue -> statement.setNull(index, Types.VARCHAR)
            else -> statement.setString(index, value.toString())
        }
    }
}
