/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT
import io.airbyte.cdk.integrations.base.JavaBaseConstants.DestinationColumns
import io.airbyte.cdk.integrations.base.JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import java.sql.SQLException
import java.util.*
import org.jooq.*
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType

abstract class JdbcSqlGeneratorIntegrationTest<DestinationState : MinimumDestinationState> :
    BaseSqlGeneratorIntegrationTest<DestinationState>() {
    protected abstract val database: JdbcDatabase
    protected abstract val structType: DataType<*>
    private val timestampWithTimeZoneType: DataType<*>
        // TODO - can we move this class into db_destinations/testFixtures?
        get() = sqlGenerator.toDialectType(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE)
    abstract override val sqlGenerator: JdbcSqlGenerator
    protected abstract val sqlDialect: SQLDialect?

    val dslContext: DSLContext
        get() = DSL.using(sqlDialect)

    /**
     * Many destinations require special handling to create JSON values. For example, redshift
     * requires you to invoke JSON_PARSE('{...}'), and postgres requires you to CAST('{...}' AS
     * JSONB). This method allows subclasses to implement that logic.
     */
    protected abstract fun toJsonValue(valueAsString: String?): Field<*>?

    @Throws(SQLException::class)
    private fun insertRecords(
        tableName: Name,
        columnNames: List<String>,
        records: List<JsonNode>,
        vararg columnsToParseJson: String
    ) {
        var insert =
            dslContext.insertInto(
                DSL.table(tableName),
                columnNames.map { columnName: String -> DSL.field(DSL.quotedName(columnName)) }
            )
        for (record in records) {
            insert =
                insert.values(
                    columnNames.map { fieldName: String ->
                        // Convert this field to a string. Pretty naive implementation.
                        val column = record[fieldName]
                        val columnAsString =
                            if (column == null) {
                                null
                            } else if (column.isTextual) {
                                column.asText()
                            } else {
                                column.toString()
                            }
                        if (Arrays.asList(*columnsToParseJson).contains(fieldName)) {
                            return@map toJsonValue(columnAsString)
                        } else {
                            return@map DSL.`val`(columnAsString)
                        }
                    }
                )
        }
        database.execute(insert.getSQL(ParamType.INLINED))
    }

    @Throws(Exception::class)
    override fun createNamespace(namespace: String) {
        database.execute(dslContext.createSchemaIfNotExists(namespace).getSQL(ParamType.INLINED))
    }

    @Throws(Exception::class)
    override fun createRawTable(streamId: StreamId) {
        val columns =
            dslContext
                .createTable(DSL.name(streamId.rawNamespace, streamId.rawName))
                .column(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false))
                .column(COLUMN_NAME_AB_EXTRACTED_AT, timestampWithTimeZoneType.nullable(false))
                .column(COLUMN_NAME_AB_LOADED_AT, timestampWithTimeZoneType)
                .column(COLUMN_NAME_DATA, structType.nullable(false))
                .column(COLUMN_NAME_AB_META, structType.nullable(true))
        if (sqlGenerator.columns == DestinationColumns.V2_WITH_GENERATION) {
            columns.column(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, SQLDataType.BIGINT)
        }
        database.execute(columns.getSQL(ParamType.INLINED))
    }

    @Throws(Exception::class)
    override fun createV1RawTable(v1RawTable: StreamId) {
        database.execute(
            dslContext
                .createTable(DSL.name(v1RawTable.rawNamespace, v1RawTable.rawName))
                .column(COLUMN_NAME_AB_ID, SQLDataType.VARCHAR(36).nullable(false))
                .column(COLUMN_NAME_EMITTED_AT, timestampWithTimeZoneType.nullable(false))
                .column(COLUMN_NAME_DATA, structType.nullable(false))
                .getSQL(ParamType.INLINED)
        )
    }

    @Throws(Exception::class)
    public override fun insertRawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        insertRecords(
            DSL.name(streamId.rawNamespace, streamId.rawName),
            sqlGenerator.columns.rawColumns,
            records,
            COLUMN_NAME_DATA,
            COLUMN_NAME_AB_META
        )
    }

    @Throws(Exception::class)
    override fun insertV1RawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        insertRecords(
            DSL.name(streamId.rawNamespace, streamId.rawName),
            LEGACY_RAW_TABLE_COLUMNS,
            records,
            COLUMN_NAME_DATA
        )
    }

    @Throws(Exception::class)
    override fun insertFinalTableRecords(
        includeCdcDeletedAt: Boolean,
        streamId: StreamId,
        suffix: String?,
        records: List<JsonNode>,
        generationId: Long,
    ) {
        val columnNames =
            (if (includeCdcDeletedAt) FINAL_TABLE_COLUMN_NAMES_CDC else FINAL_TABLE_COLUMN_NAMES)
                .toMutableList()
        if (sqlGenerator.columns == DestinationColumns.V2_WITH_GENERATION) {
            columnNames += COLUMN_NAME_AB_GENERATION_ID
        }
        insertRecords(
            DSL.name(streamId.finalNamespace, streamId.finalName + suffix),
            columnNames,
            records,
            COLUMN_NAME_AB_META,
            "struct",
            "array",
            "unknown"
        )
    }

    @Throws(Exception::class)
    override fun dumpRawTableRecords(streamId: StreamId): List<JsonNode> {
        return database.queryJsons(
            dslContext
                .selectFrom(DSL.name(streamId!!.rawNamespace, streamId.rawName))
                .getSQL(ParamType.INLINED)
        )
    }

    @Throws(Exception::class)
    override fun dumpFinalTableRecords(streamId: StreamId, suffix: String?): List<JsonNode> {
        return database.queryJsons(
            dslContext
                .selectFrom(DSL.name(streamId!!.finalNamespace, streamId.finalName + suffix))
                .getSQL(ParamType.INLINED)
        )
    }

    @Throws(Exception::class)
    override fun teardownNamespace(namespace: String) {
        database.execute(dslContext.dropSchema(namespace).cascade().getSQL(ParamType.INLINED))
    }
}
