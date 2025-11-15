/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.SourceOperations
import io.airbyte.protocol.models.JsonSchemaType
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.*
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.format.DateTimeParseException

private val LOGGER = KotlinLogging.logger {}
/** Implementation of source operations with standard JDBC types. */
open class JdbcSourceOperations :
    AbstractJdbcCompatibleSourceOperations<JDBCType>(), SourceOperations<ResultSet, JDBCType> {
    protected fun safeGetJdbcType(columnTypeInt: Int): JDBCType {
        return try {
            JDBCType.valueOf(columnTypeInt)
        } catch (e: Exception) {
            JDBCType.VARCHAR
        }
    }

    @Throws(SQLException::class)
    override fun copyToJsonField(resultSet: ResultSet, colIndex: Int, json: ObjectNode) {
        val columnTypeInt = resultSet.metaData.getColumnType(colIndex)
        val columnName = resultSet.metaData.getColumnName(colIndex)
        val columnType = safeGetJdbcType(columnTypeInt)

        when (columnType) {
            JDBCType.BIT,
            JDBCType.BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex)
            JDBCType.TINYINT,
            JDBCType.SMALLINT -> putShortInt(json, columnName, resultSet, colIndex)
            JDBCType.INTEGER -> putInteger(json, columnName, resultSet, colIndex)
            JDBCType.BIGINT -> putBigInt(json, columnName, resultSet, colIndex)
            JDBCType.FLOAT,
            JDBCType.DOUBLE -> putDouble(json, columnName, resultSet, colIndex)
            JDBCType.REAL -> putFloat(json, columnName, resultSet, colIndex)
            JDBCType.NUMERIC,
            JDBCType.DECIMAL -> putBigDecimal(json, columnName, resultSet, colIndex)
            JDBCType.CHAR,
            JDBCType.VARCHAR,
            JDBCType.LONGVARCHAR -> putString(json, columnName, resultSet, colIndex)
            JDBCType.DATE -> putDate(json, columnName, resultSet, colIndex)
            JDBCType.TIME -> putTime(json, columnName, resultSet, colIndex)
            JDBCType.TIMESTAMP -> putTimestamp(json, columnName, resultSet, colIndex)
            JDBCType.TIMESTAMP_WITH_TIMEZONE ->
                putTimestampWithTimezone(json, columnName, resultSet, colIndex)
            JDBCType.BLOB,
            JDBCType.BINARY,
            JDBCType.VARBINARY,
            JDBCType.LONGVARBINARY -> putBinary(json, columnName, resultSet, colIndex)
            JDBCType.ARRAY -> putArray(json, columnName, resultSet, colIndex)
            else -> putDefault(json, columnName, resultSet, colIndex)
        }
    }

    @Throws(SQLException::class)
    override fun setCursorField(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        cursorFieldType: JDBCType?,
        value: String?
    ) {
        when (cursorFieldType) {
            JDBCType.TIMESTAMP -> setTimestamp(preparedStatement, parameterIndex, value)
            JDBCType.TIMESTAMP_WITH_TIMEZONE ->
                setTimestampWithTimezone(preparedStatement, parameterIndex, value)
            JDBCType.TIME -> setTime(preparedStatement, parameterIndex, value)
            JDBCType.TIME_WITH_TIMEZONE ->
                setTimeWithTimezone(preparedStatement, parameterIndex, value)
            JDBCType.DATE -> setDate(preparedStatement, parameterIndex, value!!)
            JDBCType.BIT -> setBit(preparedStatement, parameterIndex, value)
            JDBCType.BOOLEAN -> setBoolean(preparedStatement, parameterIndex, value!!)
            JDBCType.TINYINT,
            JDBCType.SMALLINT -> setShortInt(preparedStatement, parameterIndex, value!!)
            JDBCType.INTEGER -> setInteger(preparedStatement, parameterIndex, value!!)
            JDBCType.BIGINT -> setBigInteger(preparedStatement, parameterIndex, value!!)
            JDBCType.FLOAT,
            JDBCType.DOUBLE -> setDouble(preparedStatement, parameterIndex, value!!)
            JDBCType.REAL -> setReal(preparedStatement, parameterIndex, value!!)
            JDBCType.NUMERIC,
            JDBCType.DECIMAL -> setDecimal(preparedStatement, parameterIndex, value!!)
            JDBCType.CHAR,
            JDBCType.NCHAR,
            JDBCType.NVARCHAR,
            JDBCType.VARCHAR,
            JDBCType.LONGVARCHAR -> setString(preparedStatement, parameterIndex, value)
            JDBCType.BINARY,
            JDBCType.BLOB -> setBinary(preparedStatement, parameterIndex, value)
            else ->
                throw IllegalArgumentException(
                    String.format("%s cannot be used as a cursor.", cursorFieldType)
                )
        }
    }

    @Throws(SQLException::class)
    protected open fun setTimestampWithTimezone(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String?
    ) {
        try {
            preparedStatement.setObject(parameterIndex, OffsetDateTime.parse(value))
        } catch (e: DateTimeParseException) {
            throw RuntimeException(e)
        }
    }

    @Throws(SQLException::class)
    protected fun setTimeWithTimezone(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String?
    ) {
        try {
            preparedStatement.setObject(parameterIndex, OffsetTime.parse(value))
        } catch (e: DateTimeParseException) {
            throw RuntimeException(e)
        }
    }

    override fun getDatabaseFieldType(field: JsonNode): JDBCType {
        try {
            return JDBCType.valueOf(field[JdbcConstants.INTERNAL_COLUMN_TYPE].asInt())
        } catch (ex: IllegalArgumentException) {
            LOGGER.warn {
                "Could not convert column: ${field[JdbcConstants.INTERNAL_COLUMN_NAME]} from table: " +
                    "${field[JdbcConstants.INTERNAL_SCHEMA_NAME]}.${field[JdbcConstants.INTERNAL_TABLE_NAME]} " +
                    "with type: ${field[JdbcConstants.INTERNAL_COLUMN_TYPE]}. Casting to VARCHAR."
            }
            return JDBCType.VARCHAR
        }
    }

    override fun isCursorType(type: JDBCType?): Boolean {
        return JdbcUtils.ALLOWED_CURSOR_TYPES.contains(type)
    }

    override fun getAirbyteType(sourceType: JDBCType): JsonSchemaType {
        return when (sourceType) {
            JDBCType.BIT,
            JDBCType.BOOLEAN -> JsonSchemaType.BOOLEAN
            JDBCType.TINYINT,
            JDBCType.SMALLINT -> JsonSchemaType.INTEGER
            JDBCType.INTEGER -> JsonSchemaType.INTEGER
            JDBCType.BIGINT -> JsonSchemaType.INTEGER
            JDBCType.FLOAT,
            JDBCType.DOUBLE -> JsonSchemaType.NUMBER
            JDBCType.REAL -> JsonSchemaType.NUMBER
            JDBCType.NUMERIC,
            JDBCType.DECIMAL -> JsonSchemaType.NUMBER
            JDBCType.CHAR,
            JDBCType.NCHAR,
            JDBCType.NVARCHAR,
            JDBCType.VARCHAR,
            JDBCType.LONGVARCHAR -> JsonSchemaType.STRING
            JDBCType.DATE -> JsonSchemaType.STRING
            JDBCType.TIME -> JsonSchemaType.STRING
            JDBCType.TIMESTAMP -> JsonSchemaType.STRING
            JDBCType.BLOB,
            JDBCType.BINARY,
            JDBCType.VARBINARY,
            JDBCType.LONGVARBINARY -> JsonSchemaType.STRING_BASE_64
            JDBCType.ARRAY -> JsonSchemaType.ARRAY
            else -> JsonSchemaType.STRING
        }
    }

    companion object {}
}
