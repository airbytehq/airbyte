/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.component

import io.airbyte.cdk.load.component.TestTableOperationsClient
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
import io.airbyte.cdk.load.util.Jsons
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import javax.sql.DataSource

/**
 * JDBC-based [TestTableOperationsClient] for Redshift component tests. Uses the shared [DataSource]
 * for all database operations.
 *
 * Follows the same pattern as `PostgresTestTableOperationsClient`: column types are introspected
 * from `information_schema.columns` so that `super` columns receive JSON strings while other
 * columns use type-specific JDBC setters.
 */
@Requires(env = ["component"])
@Singleton
class RedshiftTestTableOperationsClient(
    private val dataSource: DataSource,
) : TestTableOperationsClient {

    override suspend fun ping() {
        dataSource.connection.use { conn -> conn.createStatement().use { it.execute("SELECT 1") } }
    }

    override suspend fun dropNamespace(namespace: String) {
        dataSource.connection.use { conn ->
            conn.createStatement().use {
                it.execute("DROP SCHEMA IF EXISTS \"$namespace\" CASCADE")
            }
        }
    }

    override suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) {
        if (records.isEmpty()) return

        // Get column types from database to handle super columns properly
        val columnTypes = getColumnTypes(table)

        // Get all unique columns from ALL records to handle sparse data (e.g., CDC deletion column)
        val columns = records.flatMap { it.keys }.distinct().toList()
        val columnNames = columns.joinToString(", ") { "\"$it\"" }
        val placeholders = columns.indices.joinToString(", ") { "?" }

        val sql =
            """INSERT INTO "${table.namespace}"."${table.name}" ($columnNames) VALUES ($placeholders)"""

        dataSource.connection.use { conn ->
            conn.prepareStatement(sql).use { ps ->
                for (record in records) {
                    columns.forEachIndexed { index, column ->
                        val value = record[column]
                        val columnType = columnTypes[column]
                        setParameterValue(ps, index + 1, value, columnType)
                    }
                    ps.addBatch()
                }
                ps.executeBatch()
            }
        }
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery("""SELECT * FROM "${table.namespace}"."${table.name}"""").use { rs
                    ->
                    val meta = rs.metaData
                    val result = mutableListOf<Map<String, Any>>()
                    while (rs.next()) {
                        val row = mutableMapOf<String, Any>()
                        for (i in 1..meta.columnCount) {
                            val name = meta.getColumnName(i)
                            val typeName = meta.getColumnTypeName(i).lowercase()
                            val value = readColumn(rs, i, typeName)
                            if (value != null) {
                                row[name] = value
                            }
                        }
                        result.add(row)
                    }
                    return result
                }
            }
        }
    }

    // ================================================================
    // Insert helpers
    // ================================================================

    /** Queries `information_schema.columns` to build a column-name → data-type map. */
    private fun getColumnTypes(table: TableName): Map<String, String> {
        val columnTypes = mutableMapOf<String, String>()
        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt
                    .executeQuery(
                        """
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = '${table.namespace}'
                          AND table_name = '${table.name}'
                        """
                    )
                    .use { rs ->
                        while (rs.next()) {
                            columnTypes[rs.getString("column_name")] = rs.getString("data_type")
                        }
                    }
            }
        }
        return columnTypes
    }

    /**
     * Binds an [AirbyteValue] into a [java.sql.PreparedStatement] at the given 1-based index.
     *
     * If the target column is `super`, the value is serialized to a JSON string so that Redshift
     * can auto-parse it. If the target column is `character varying`, all values are converted to
     * strings (handles schema evolution where a SUPER column becomes VARCHAR). Otherwise,
     * type-specific JDBC setters are used.
     */
    private fun setParameterValue(
        ps: java.sql.PreparedStatement,
        index: Int,
        value: AirbyteValue?,
        columnType: String?,
    ) {
        // Handle nulls once -- SUPER columns need Types.OTHER, everything else uses Types.NULL.
        if (value == null || value is NullValue) {
            val sqlType = if (columnType == "super") java.sql.Types.OTHER else java.sql.Types.NULL
            ps.setNull(index, sqlType)
            return
        }

        // SUPER columns: serialize any value as JSON; Redshift auto-parses the string.
        if (columnType == "super") {
            ps.setString(index, serializeValue(value, asJson = true))
            return
        }

        // VARCHAR columns: convert any value to string.
        // After schema evolution (e.g. SUPER → VARCHAR), the AirbyteValue may still be
        // BooleanValue/IntegerValue/ObjectValue, but the target column is now VARCHAR.
        // Redshift does not implicitly cast boolean/integer to varchar, so we must use setString.
        if (columnType?.startsWith("character varying") == true) {
            ps.setString(index, serializeValue(value, asJson = false))
            return
        }

        when (value) {
            is StringValue -> ps.setString(index, value.value)
            is IntegerValue -> ps.setLong(index, value.value.toLong())
            is NumberValue -> ps.setBigDecimal(index, value.value)
            is BooleanValue -> ps.setBoolean(index, value.value)
            is TimestampWithTimezoneValue -> {
                val odt = OffsetDateTime.parse(value.value.toString())
                ps.setObject(index, odt)
            }
            is TimestampWithoutTimezoneValue -> {
                val ldt = java.time.LocalDateTime.parse(value.value.toString())
                ps.setObject(index, ldt)
            }
            is DateValue -> {
                val ld = java.time.LocalDate.parse(value.value.toString())
                ps.setObject(index, ld)
            }
            is TimeWithTimezoneValue -> ps.setString(index, value.value.toString())
            is TimeWithoutTimezoneValue -> {
                val lt = java.time.LocalTime.parse(value.value.toString())
                ps.setObject(index, lt)
            }
            is ObjectValue -> ps.setString(index, serializeValue(value, asJson = true))
            is ArrayValue -> ps.setString(index, serializeValue(value, asJson = true))
            is NullValue -> {} // already handled above
        }
    }

    /**
     * Converts an [AirbyteValue] to a string.
     *
     * When [asJson] is `true` (for SUPER columns), strings and temporal values are JSON-quoted so
     * that Redshift can parse the result as a valid JSON literal. When `false` (for VARCHAR
     * columns), plain text is returned.
     */
    private fun serializeValue(value: AirbyteValue, asJson: Boolean): String =
        when (value) {
            is NullValue -> "null"
            is StringValue -> if (asJson) Jsons.writeValueAsString(value.value) else value.value
            is IntegerValue -> value.value.toString()
            is NumberValue -> value.value.toPlainString()
            is BooleanValue -> value.value.toString()
            is ObjectValue -> Jsons.writeValueAsString(value.values)
            is ArrayValue -> Jsons.writeValueAsString(value.values)
            is DateValue ->
                if (asJson) Jsons.writeValueAsString(value.value.toString())
                else value.value.toString()
            is TimestampWithTimezoneValue ->
                if (asJson) Jsons.writeValueAsString(value.value.toString())
                else value.value.toString()
            is TimestampWithoutTimezoneValue ->
                if (asJson) Jsons.writeValueAsString(value.value.toString())
                else value.value.toString()
            is TimeWithTimezoneValue ->
                if (asJson) Jsons.writeValueAsString(value.value.toString())
                else value.value.toString()
            is TimeWithoutTimezoneValue ->
                if (asJson) Jsons.writeValueAsString(value.value.toString())
                else value.value.toString()
        }

    // ================================================================
    // Read helpers
    // ================================================================

    /** Reads a single column value from a [java.sql.ResultSet], applying Redshift type mapping. */
    private fun readColumn(
        rs: java.sql.ResultSet,
        index: Int,
        typeName: String,
    ): Any? =
        when (typeName) {
            "timestamptz" ->
                rs.getTimestamp(index)?.let {
                    it.toInstant()
                        .atOffset(ZoneOffset.UTC)
                        .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
                }
            "timestamp" -> rs.getTimestamp(index)?.toLocalDateTime()?.toString()
            "date" -> rs.getDate(index)?.toString()
            "time" -> rs.getTime(index)?.toLocalTime()?.toString()
            "timetz" -> rs.getString(index)
            "super" ->
                rs.getString(index)?.let { json ->
                    val parsed = Jsons.readValue(json, Any::class.java)
                    // Jackson deserializes small integers as Integer; normalize to Long
                    if (parsed is Integer) parsed.toLong() else parsed
                }
            "numeric" -> rs.getBigDecimal(index)
            else -> rs.getObject(index)
        }
}
