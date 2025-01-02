/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampValue

import io.airbyte.cdk.load.data.UnknownValue
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.util.TimeStringUtility.toLocalDate
import io.airbyte.cdk.load.util.TimeStringUtility.toLocalDateTime
import io.airbyte.cdk.load.util.TimeStringUtility.toOffset
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.convert.AirbyteTypeToSqlType
import io.airbyte.integrations.destination.mssql.v2.convert.AirbyteValueToSqlValue
import io.airbyte.integrations.destination.mssql.v2.convert.ResultSetToAirbyteValue.Companion.getAirbyteNamedValue
import io.airbyte.integrations.destination.mssql.v2.convert.SqlTypeToMssqlType
import io.airbyte.protocol.models.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.Jsons
import java.lang.ArithmeticException
import java.sql.Date
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.Time
import java.sql.Timestamp
import java.sql.Types
import java.time.Instant
import java.time.format.DateTimeParseException
import java.util.UUID

class MSSQLQueryBuilder(
    config: MSSQLConfiguration,
    private val stream: DestinationStream,
) {

    companion object {
        val AIRBYTE_RAW_ID = "_airbyte_raw_id"
        val AIRBYTE_EXTRACTED_AT = "_airbyte_extracted_at"
        val AIRBYTE_META = "_airbyte_meta"
        val AIRBYTE_GENERATION_ID = "_airbyte_generation_id"

        val airbyteFinalTableFields =
            listOf(
                NamedField(AIRBYTE_RAW_ID, FieldType(StringType, false)),
                NamedField(AIRBYTE_EXTRACTED_AT, FieldType(TimestampTypeWithoutTimezone, false)),
                NamedField(AIRBYTE_META, FieldType(ObjectTypeWithoutSchema, false)),
                NamedField(AIRBYTE_GENERATION_ID, FieldType(IntegerType, false)),
            )

        val airbyteFields = airbyteFinalTableFields.map { it.name }.toSet()

    }

    data class NamedField(val name: String, val type: FieldType)
    data class NamedValue(val name: String, val value: AirbyteValue)

    private val internalSchema: String = config.rawDataSchema
    private val outputSchema: String = stream.descriptor.namespace ?: config.schema
    private val tableName: String = stream.descriptor.name
    private val fqTableName = "$outputSchema.$tableName"

    val finalTableSchema: List<NamedField> =
        airbyteFinalTableFields + extractFinalTableSchema(stream.schema)

    fun createFinalTableIfNotExists(): String =
        createTableIfNotExists(fqTableName, finalTableSchema)

    fun createFinalSchemaIfNotExists(): String = createSchemaIfNotExists(outputSchema)

    fun getFinalTableInsertColumnHeader(): String =
        getFinalTableInsertColumnHeader(fqTableName, finalTableSchema)

    fun populateStatement(
        statement: PreparedStatement,
        record: DestinationRecordAirbyteValue,
        schema: List<NamedField>
    ) {
        val toSqlType = AirbyteTypeToSqlType()
        val toSqlValue = AirbyteValueToSqlValue()
        val recordObject = record.data as ObjectValue

        var airbyteMetaStatementIndex: Int? = null
        val airbyteMeta =
            AirbyteRecordMessageMeta().apply {
                changes = mutableListOf()
                setAdditionalProperty("syncId", stream.syncId)
            }
        schema.forEachIndexed { index, field ->
            val stmntIdx = index + 1
            val value = recordObject.values[field.name]
            val sqlType = toSqlType.convert(field.type.type)

            if (value == null) {
                if (field.name in airbyteFields) {
                    when (field.name) {
                        AIRBYTE_RAW_ID ->
                            statement.setString(stmntIdx, UUID.randomUUID().toString())
                        AIRBYTE_EXTRACTED_AT ->
                            statement.setTimestamp(
                                stmntIdx,
                                Timestamp.from(Instant.ofEpochMilli(record.emittedAtMs))
                            )
                        AIRBYTE_GENERATION_ID -> statement.setLong(stmntIdx, stream.generationId)
                        AIRBYTE_META -> airbyteMetaStatementIndex = stmntIdx
                    }
                } else {
                    statement.setNull(stmntIdx, sqlType)
                }
            } else {
                try {
                    when (value) {
                        is ObjectValue ->
                            statement.setString(
                                stmntIdx,
                                Jsons.serialize(toSqlValue.convert(value))
                            )

                        is ArrayValue ->
                            statement.setString(
                                stmntIdx,
                                Jsons.serialize(toSqlValue.convert(value))
                            )

                        is BooleanValue -> statement.setBoolean(stmntIdx, value.value)
                        is DateValue ->
                            statement.setDate(stmntIdx, Date.valueOf(toLocalDate((value.value))))

                        is IntegerValue -> statement.setLong(stmntIdx, value.value.longValueExact())
                        NullValue -> statement.setNull(stmntIdx, sqlType)
                        is NumberValue -> statement.setDouble(stmntIdx, value.value.toDouble())
                        is StringValue ->
                            if (sqlType == Types.VARCHAR || sqlType == Types.LONGVARCHAR) {
                                statement.setString(stmntIdx, value.value)
                            } else {
                                throw IllegalArgumentException()
                            }

                        is TimeValue ->
                            statement.setTime(stmntIdx, Time.valueOf(toOffset(value.value)))

                        is TimestampValue ->
                            statement.setTimestamp(
                                stmntIdx,
                                Timestamp.valueOf(toLocalDateTime(value.value))
                            )

                        is UnknownValue ->
                            statement.setString(stmntIdx, Jsons.serialize(value.value))
                    }
                } catch (e: ArithmeticException) {
                    statement.setNull(stmntIdx, sqlType)
                    airbyteMeta.changes.add(
                        AirbyteRecordMessageMetaChange()
                            .withField(field.name)
                            .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                            .withReason(
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_FIELD_SIZE_LIMITATION
                            )
                    )
                } catch (e: DateTimeParseException) {
                    statement.setNull(stmntIdx, sqlType)
                    airbyteMeta.changes.add(
                        AirbyteRecordMessageMetaChange()
                            .withField(field.name)
                            .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                            .withReason(
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR
                            )
                    )
                } catch (e: IllegalArgumentException) {
                    statement.setNull(stmntIdx, sqlType)
                    airbyteMeta.changes.add(
                        AirbyteRecordMessageMetaChange()
                            .withField(field.name)
                            .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                            .withReason(
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR
                            )
                    )
                }
            }
        }
        airbyteMetaStatementIndex?.let { statementIndex ->
            statement.setString(statementIndex, Jsons.serialize(airbyteMeta))
        }
    }

    fun readResult(rs: ResultSet, schema: List<NamedField>): ObjectValue {
        val valueMap =
            schema
                .filter { field -> field.name !in airbyteFields }
                .map { field -> rs.getAirbyteNamedValue(field) }
                .associate { it.name to it.value }
        return ObjectValue.from(valueMap)
    }

    fun selectAllRecords(): String = "SELECT * FROM $fqTableName"

    private fun createSchemaIfNotExists(schema: String): String =
        """
            IF NOT EXISTS (SELECT name FROM sys.schemas WHERE name = '$schema')
            BEGIN
                EXEC ('CREATE SCHEMA $schema');
            END
        """.trimIndent()

    private fun createTableIfNotExists(fqTableName: String, schema: List<NamedField>): String =
        """
            IF OBJECT_ID('$fqTableName') IS NULL
            BEGIN
                CREATE TABLE $fqTableName
                (
                    ${airbyteTypeToSqlSchema(schema, separator = ",\n                    ")}
                );
            END
        """.trimIndent()

    private fun getFinalTableInsertColumnHeader(
        fqTableName: String,
        schema: List<NamedField>
    ): String {
        return StringBuilder()
            .apply {
                append("INSERT INTO $fqTableName(")
                append(schema.map { it.name }.joinToString(", "))
                append(") VALUES (")
                append(schema.map { "?" }.joinToString(", "))
                append(")")
            }
            .toString()
    }

    private fun extractFinalTableSchema(schema: AirbyteType): List<NamedField> =
        when (schema) {
            is ObjectType -> {
                (stream.schema as ObjectType)
                    .properties
                    .map { NamedField(name = it.key, type = it.value) }
                    .toList()
            }
            else -> TODO("most likely fail hard")
        }

    private fun airbyteTypeToSqlSchema(schema: List<NamedField>, separator: String): String {
        val toSqlType = AirbyteTypeToSqlType()
        val toMssqlType = SqlTypeToMssqlType()
        return schema
            .map {
                "${it.name} ${toMssqlType.convert(toSqlType.convert(it.type.type)).sqlString} NULL"
            }
            .joinToString(separator = separator)
    }
}
