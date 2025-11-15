package io.airbyte.integrations.destination.mysql.component

import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.table.TableName
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.sql.Date
import java.sql.PreparedStatement
import java.sql.Timestamp
import java.sql.Types
import javax.sql.DataSource

@Requires(env = ["component"])
@Singleton
class MySQLTestTableOperationsClient(
    private val dataSource: DataSource,
) : TestTableOperationsClient {

    override suspend fun ping() {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.executeQuery("SELECT 1")
            }
        }
    }

    override suspend fun dropNamespace(namespace: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                // MySQL uses databases as namespaces
                statement.execute("DROP DATABASE IF EXISTS `${namespace}`")
            }
        }
    }

    override suspend fun insertRecords(
        table: TableName,
        records: List<Map<String, AirbyteValue>>
    ) {
        if (records.isEmpty()) return

        dataSource.connection.use { connection ->
            records.forEach { record ->
                val columns = record.keys.joinToString(", ") { "`$it`" }
                val placeholders = record.keys.joinToString(", ") { "?" }
                val sql = """
                    INSERT INTO `${table.namespace}`.`${table.name}` ($columns)
                    VALUES ($placeholders)
                """

                connection.prepareStatement(sql).use { statement ->
                    record.values.forEachIndexed { index, value ->
                        setParameter(statement, index + 1, value)
                    }
                    statement.executeUpdate()
                }
            }
        }
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        val results = mutableListOf<Map<String, Any>>()

        dataSource.connection.use { connection ->
            val sql = "SELECT * FROM `${table.namespace}`.`${table.name}`"
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sql)
                val metadata = rs.metaData

                while (rs.next()) {
                    val row = mutableMapOf<String, Any>()
                    for (i in 1..metadata.columnCount) {
                        val columnName = metadata.getColumnName(i)
                        val value = rs.getObject(i)
                        if (value != null) {
                            row[columnName] = value
                        }
                    }
                    results.add(row)
                }
            }
        }

        return results
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
