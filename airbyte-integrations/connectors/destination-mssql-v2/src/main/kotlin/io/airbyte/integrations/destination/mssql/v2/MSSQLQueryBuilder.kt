/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import com.microsoft.sqlserver.jdbc.SQLServerException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.convert.AirbyteTypeToSqlType
import io.airbyte.integrations.destination.mssql.v2.convert.AirbyteValueToStatement.Companion.setAsNullValue
import io.airbyte.integrations.destination.mssql.v2.convert.AirbyteValueToStatement.Companion.setValue
import io.airbyte.integrations.destination.mssql.v2.convert.MssqlType
import io.airbyte.integrations.destination.mssql.v2.convert.ResultSetToAirbyteValue.Companion.getAirbyteNamedValue
import io.airbyte.integrations.destination.mssql.v2.convert.SqlTypeToMssqlType
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.ArithmeticException
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.util.UUID

private val logger = KotlinLogging.logger {}

fun <T> String.executeQuery(connection: Connection, vararg args: String, f: (ResultSet) -> T): T {
    logger.debug { "EXECUTING SQL:\n$this" }

    connection.prepareStatement(this.trimIndent()).use { statement ->
        args.forEachIndexed { index, arg -> statement.setString(index + 1, arg) }
        return statement.executeQuery().use(f)
    }
}

fun String.executeUpdate(connection: Connection, f: (PreparedStatement) -> Unit) {
    logger.debug { "EXECUTING SQL:\n$this" }

    connection.prepareStatement(this.trimIndent()).use(f)
}

fun String.executeUpdate(connection: Connection, vararg args: String) {
    this.executeUpdate(connection) { statement ->
        args.forEachIndexed { index, arg -> statement.setString(index + 1, arg) }
        statement.executeUpdate()
    }
}

fun String.toQuery(vararg args: String): String = this.trimIndent().replace("?", "%s").format(*args)

fun String.toQuery(context: Map<String, String>): String =
    this.trimIndent().replace(VAR_REGEX) {
        context[it.groupValues[1]] ?: throw IllegalStateException("Context is missing ${it.value}")
    }

private val VAR_REGEX = "\\?(\\w+)".toRegex()

private const val SCHEMA_KEY = "schema"
private const val TABLE_KEY = "table"
private const val COLUMNS_KEY = "columns"
private const val TEMPLATE_COLUMNS_KEY = "templateColumns"
private const val UNIQUENESS_CONSTRAINT_KEY = "uniquenessConstraint"
private const val UPDATE_STATEMENT_KEY = "updateStatement"
private const val INDEX_KEY = "index"
private const val SECONDARY_INDEX_KEY = "secondaryIndex"

const val GET_EXISTING_SCHEMA_QUERY =
    """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION ASC
    """

const val CREATE_SCHEMA_QUERY =
    """
        DECLARE @Schema VARCHAR(MAX) = ?
        IF NOT EXISTS (SELECT name FROM sys.schemas WHERE name = @Schema)
        BEGIN
            EXEC ('CREATE SCHEMA [' + @Schema + ']');
        END
    """

const val CREATE_TABLE_QUERY =
    """
        IF OBJECT_ID('?$SCHEMA_KEY.?$TABLE_KEY') IS NULL
        BEGIN
            CREATE TABLE [?$SCHEMA_KEY].[?$TABLE_KEY]
            (
                ?$COLUMNS_KEY
            );
            ?$INDEX_KEY;
            ?$SECONDARY_INDEX_KEY;
        END
    """

const val CREATE_INDEX_QUERY =
    """
        CREATE ? INDEX ? ON [?].[?] (?)
    """

const val INSERT_INTO_QUERY =
    """
        INSERT INTO [?$SCHEMA_KEY].[?$TABLE_KEY] (?$COLUMNS_KEY)
            SELECT table_value.*
            FROM (VALUES (?$TEMPLATE_COLUMNS_KEY)) table_value(?$COLUMNS_KEY)
    """

const val MERGE_INTO_QUERY =
    """
        MERGE INTO [?$SCHEMA_KEY].[?$TABLE_KEY] AS Target
        USING (VALUES (?$TEMPLATE_COLUMNS_KEY)) AS Source (?$COLUMNS_KEY)
        ON ?$UNIQUENESS_CONSTRAINT_KEY
        WHEN MATCHED THEN
            UPDATE SET ?$UPDATE_STATEMENT_KEY
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (?$COLUMNS_KEY) VALUES (?$COLUMNS_KEY)
        ;
    """

const val ALTER_TABLE_ADD =
    """
        ALTER TABLE [?].[?]
        ADD [?] ? NULL;
    """
const val ALTER_TABLE_DROP =
    """
        ALTER TABLE [?].[?]
        DROP COLUMN [?];
    """
const val ALTER_TABLE_MODIFY =
    """
        ALTER TABLE [?].[?]
        ALTER COLUMN [?] ? NULL;
    """

const val DELETE_WHERE_COL_IS_NOT_NULL =
    """
        DELETE FROM [?].[?]
        WHERE [?] is not NULL
    """

const val DELETE_WHERE_COL_LESS_THAN =
    """
        DELETE FROM [?].[?]
        WHERE [?] < ?
    """

const val SELECT_FROM =
    """
        SELECT *
        FROM [?].[?]
    """

class MSSQLQueryBuilder(
    config: MSSQLConfiguration,
    private val stream: DestinationStream,
) {
    companion object {

        const val SQL_ERROR_OBJECT_EXISTS = 2714

        const val AIRBYTE_RAW_ID = "_airbyte_raw_id"
        const val AIRBYTE_EXTRACTED_AT = "_airbyte_extracted_at"
        const val AIRBYTE_META = "_airbyte_meta"
        const val AIRBYTE_GENERATION_ID = "_airbyte_generation_id"
        const val AIRBYTE_CDC_DELETED_AT = "_ab_cdc_deleted_at"
        const val DEFAULT_SEPARATOR = ",\n        "

        val airbyteFinalTableFields =
            listOf(
                NamedField(AIRBYTE_RAW_ID, FieldType(StringType, false)),
                NamedField(AIRBYTE_EXTRACTED_AT, FieldType(IntegerType, false)),
                NamedField(AIRBYTE_META, FieldType(ObjectTypeWithoutSchema, false)),
                NamedField(AIRBYTE_GENERATION_ID, FieldType(IntegerType, false)),
            )

        val airbyteFields = airbyteFinalTableFields.map { it.name }.toSet()

        private fun AirbyteRecordMessageMeta.trackChange(
            fieldName: String,
            change: AirbyteRecordMessageMetaChange.Change,
            reason: AirbyteRecordMessageMetaChange.Reason,
        ) {
            this.changes.add(
                AirbyteRecordMessageMetaChange()
                    .withField(fieldName)
                    .withChange(change)
                    .withReason(reason)
            )
        }
    }

    data class NamedField(val name: String, val type: FieldType)
    data class NamedValue(val name: String, val value: AirbyteValue)
    data class NamedSqlField(val name: String, val type: MssqlType)

    val outputSchema: String = stream.descriptor.namespace ?: config.schema
    val tableName: String = stream.descriptor.name
    private val uniquenessKey: List<String> =
        when (stream.importType) {
            is Dedupe ->
                if ((stream.importType as Dedupe).primaryKey.isNotEmpty()) {
                    (stream.importType as Dedupe).primaryKey.map { it.joinToString(".") }
                } else {
                    listOf((stream.importType as Dedupe).cursor.joinToString("."))
                }
            Append -> emptyList()
            Overwrite -> emptyList()
        }

    private val toSqlType = AirbyteTypeToSqlType()
    private val toMssqlType = SqlTypeToMssqlType()

    val finalTableSchema: List<NamedField> =
        airbyteFinalTableFields + extractFinalTableSchema(stream.schema)
    val hasCdc: Boolean = finalTableSchema.any { it.name == AIRBYTE_CDC_DELETED_AT }

    private fun getExistingSchema(connection: Connection): List<NamedSqlField> {
        val fields = mutableListOf<NamedSqlField>()
        GET_EXISTING_SCHEMA_QUERY.executeQuery(connection, outputSchema, tableName) { rs ->
            while (rs.next()) {
                val name = rs.getString("COLUMN_NAME")
                val type = MssqlType.valueOf(rs.getString("DATA_TYPE").uppercase())
                fields.add(NamedSqlField(name, type))
            }
        }
        return fields
    }

    private fun getSchema(): List<NamedSqlField> =
        finalTableSchema.map {
            NamedSqlField(it.name, toMssqlType.convert(toSqlType.convert(it.type.type)))
        }

    fun updateSchema(connection: Connection) {
        val existingSchema = getExistingSchema(connection)
        val expectedSchema = getSchema()

        val existingFields = existingSchema.associate { it.name to it.type }
        val expectedFields = expectedSchema.associate { it.name to it.type }

        if (existingFields == expectedFields) {
            return
        }

        val toDelete = existingFields.filter { it.key !in expectedFields }
        val toAdd = expectedFields.filter { it.key !in existingFields }
        val toAlter =
            expectedFields.filter { it.key in existingFields && it.value != existingFields[it.key] }

        val query =
            StringBuilder()
                .apply {
                    toDelete.entries.forEach {
                        appendLine(ALTER_TABLE_DROP.toQuery(outputSchema, tableName, it.key))
                    }
                    toAdd.entries.forEach {
                        appendLine(ALTER_TABLE_ADD
                            .toQuery(outputSchema, tableName, it.key, it.value.sqlString))
                    }
                    toAlter.entries.forEach {
                        appendLine(
                            ALTER_TABLE_MODIFY
                                .toQuery(outputSchema, tableName, it.key, it.value.sqlString)
                        )
                    }
                }
                .toString()

        query.executeUpdate(connection)
    }

    fun createTableIfNotExists(connection: Connection) {
        try {
            CREATE_SCHEMA_QUERY.executeUpdate(connection, outputSchema)
        } catch (e: SQLServerException) {
            // MSSQL create schema if not exists isn't atomic. Ignoring this error when it happens.
            if (e.sqlServerError.errorNumber != SQL_ERROR_OBJECT_EXISTS) {
                throw e
            }
        }

        createTableIfNotExistsQuery(finalTableSchema).executeUpdate(connection)
    }

    fun getFinalTableInsertColumnHeader(): String =
        getFinalTableInsertColumnHeader(finalTableSchema)

    fun deleteCdc(connection: Connection) =
        DELETE_WHERE_COL_IS_NOT_NULL.toQuery(outputSchema, tableName, AIRBYTE_CDC_DELETED_AT)
            .executeUpdate(connection)

    fun deletePreviousGenerations(connection: Connection, minGenerationId: Long) =
        DELETE_WHERE_COL_LESS_THAN.toQuery(
                outputSchema,
                tableName,
                AIRBYTE_GENERATION_ID,
                minGenerationId.toString()
            )
            .executeUpdate(connection)

    fun populateStatement(
        statement: PreparedStatement,
        record: DestinationRecordAirbyteValue,
        schema: List<NamedField>
    ) {
        val recordObject = record.data as ObjectValue
        var airbyteMetaStatementIndex: Int? = null
        val airbyteMeta =
            AirbyteRecordMessageMeta().apply {
                changes =
                    record.meta?.changes?.map { it.asProtocolObject() }?.toMutableList()
                        ?: mutableListOf()
                setAdditionalProperty("syncId", stream.syncId)
            }

        schema.forEachIndexed { index, field ->
            val statementIndex = index + 1
            if (field.name in airbyteFields) {
                when (field.name) {
                    AIRBYTE_RAW_ID ->
                        statement.setString(statementIndex, UUID.randomUUID().toString())
                    AIRBYTE_EXTRACTED_AT -> statement.setLong(statementIndex, record.emittedAtMs)
                    AIRBYTE_GENERATION_ID -> statement.setLong(statementIndex, stream.generationId)
                    AIRBYTE_META -> airbyteMetaStatementIndex = statementIndex
                }
            } else {
                try {
                    val value = recordObject.values[field.name]
                    statement.setValue(statementIndex, value, field)
                } catch (e: Exception) {
                    statement.setAsNullValue(statementIndex, field.type.type)
                    when (e) {
                        is ArithmeticException ->
                            airbyteMeta.trackChange(
                                field.name,
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_FIELD_SIZE_LIMITATION,
                            )
                        else ->
                            airbyteMeta.trackChange(
                                field.name,
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR,
                            )
                    }
                }
            }
        }
        airbyteMetaStatementIndex?.let { statementIndex ->
            if (airbyteMeta.changes.isEmpty()) {
                airbyteMeta.changes = null
            }
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

    private fun createTableIfNotExistsQuery(schema: List<NamedField>): String {
        val fqTableName = "$outputSchema.$tableName"
        val index =
            if (uniquenessKey.isNotEmpty())
                createIndex(fqTableName, uniquenessKey, clustered = false)
            else ""
        val cdcIndex = if (hasCdc) createIndex(fqTableName, listOf(AIRBYTE_CDC_DELETED_AT)) else ""

        return CREATE_TABLE_QUERY
            .toQuery(mapOf(
                SCHEMA_KEY to outputSchema,
                TABLE_KEY to tableName,
                COLUMNS_KEY to airbyteTypeToSqlSchema(schema),
                INDEX_KEY to index,
                SECONDARY_INDEX_KEY to cdcIndex,
            ))
    }

    private fun createIndex(
        fqTableName: String,
        columns: List<String>,
        clustered: Boolean = false
    ): String {
        val name = "${fqTableName.replace('.', '_')}_${columns.hashCode()}"
        val indexType = if (clustered) "CLUSTERED" else ""
        return CREATE_INDEX_QUERY
            .toQuery(indexType, name, outputSchema, tableName, columns.joinToString(", "))
    }

    private fun getFinalTableInsertColumnHeader(
        schema: List<NamedField>
    ): String {
        val columns = schema.joinToString(", ") { "[${it.name}]" }
        val templateColumns = schema.joinToString(", ") { "?" }
        return if (uniquenessKey.isEmpty()) {
            INSERT_INTO_QUERY
                .toQuery(mapOf(
                    SCHEMA_KEY to outputSchema,
                    TABLE_KEY to tableName,
                    COLUMNS_KEY to columns,
                    TEMPLATE_COLUMNS_KEY to templateColumns,
                ))
        } else {
            val uniquenessConstraint =
                uniquenessKey.joinToString(" AND ") { "Target.[$it] = Source.[$it]" }
            val updateStatement = schema.joinToString(", ") { "Target.[${it.name}] = Source.[${it.name}]" }
            MERGE_INTO_QUERY
                .toQuery(mapOf(
                    SCHEMA_KEY to outputSchema,
                    TABLE_KEY to tableName,
                    TEMPLATE_COLUMNS_KEY to templateColumns,
                    COLUMNS_KEY to columns,
                    UNIQUENESS_CONSTRAINT_KEY to uniquenessConstraint,
                    UPDATE_STATEMENT_KEY to updateStatement,
                ))
        }
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

    private fun airbyteTypeToSqlSchema(
        schema: List<NamedField>,
        separator: String = DEFAULT_SEPARATOR
    ): String {
        return schema.joinToString(separator = separator) {
            "[${it.name}] ${toMssqlType.convert(toSqlType.convert(it.type.type)).sqlString} NULL"
        }
    }
}
