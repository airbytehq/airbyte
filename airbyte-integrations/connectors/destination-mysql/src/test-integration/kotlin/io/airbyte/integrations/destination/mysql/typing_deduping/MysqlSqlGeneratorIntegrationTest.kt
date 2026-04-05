/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.mysql.MySQLDestination
import io.airbyte.integrations.destination.mysql.MySQLNameTransformer
import io.airbyte.integrations.destination.mysql.MysqlTestDatabase
import io.airbyte.integrations.destination.mysql.MysqlTestSourceOperations
import io.airbyte.integrations.destination.mysql.typing_deduping.MysqlSqlGenerator.Companion.TIMESTAMP_FORMATTER
import java.time.OffsetDateTime
import java.util.Optional
import org.jooq.DataType
import org.jooq.Field
import org.jooq.SQLDialect
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

class MysqlSqlGeneratorIntegrationTest :
    JdbcSqlGeneratorIntegrationTest<MinimumDestinationState>() {

    override val sqlDialect: SQLDialect = SQLDialect.MYSQL
    override val sqlGenerator: JdbcSqlGenerator = MysqlSqlGenerator()
    override val structType: DataType<*> = MysqlSqlGenerator.JSON_TYPE
    override val supportsSafeCast: Boolean = false
    override val database = Companion.database
    override val destinationHandler: DestinationHandler<MinimumDestinationState>
        // lazy init. We need `namespace` to be initialized before this call.
        get() = MysqlDestinationHandler(Companion.database, namespace)

    @Throws(Exception::class)
    override fun insertRawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        reformatMetaColumnTimestamps(records)
        super.insertRawTableRecords(streamId, records)
    }

    @Throws(Exception::class)
    override fun insertFinalTableRecords(
        includeCdcDeletedAt: Boolean,
        streamId: StreamId,
        suffix: String?,
        records: List<JsonNode>
    ) {
        reformatMetaColumnTimestamps(records)
        super.insertFinalTableRecords(includeCdcDeletedAt, streamId, suffix, records)
    }

    @Throws(Exception::class)
    override fun insertV1RawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        reformatMetaColumnTimestamps(records)
        super.insertV1RawTableRecords(streamId, records)
    }

    @Throws(Exception::class)
    override fun createRawTable(streamId: StreamId) {
        database.execute(
            dslContext
                .createTable(DSL.name(streamId.rawNamespace, streamId.rawName))
                .column(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(256).nullable(false))
                .column(COLUMN_NAME_DATA, structType.nullable(false))
                // we use VARCHAR for timestamp values, but TIMESTAMP(6) for extracted+loaded_at.
                // because legacy normalization did that. :shrug:
                .column(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMP(6).nullable(false))
                .column(COLUMN_NAME_AB_LOADED_AT, SQLDataType.TIMESTAMP(6))
                .column(COLUMN_NAME_AB_META, structType.nullable(true))
                .getSQL(ParamType.INLINED),
        )
    }

    @Throws(Exception::class)
    override fun createV1RawTable(v1RawTable: StreamId) {
        database.execute(
            dslContext
                .createTable(DSL.name(v1RawTable.rawNamespace, v1RawTable.rawName))
                .column(
                    COLUMN_NAME_AB_ID,
                    SQLDataType.VARCHAR(36).nullable(false),
                ) // similar to createRawTable - this data type is timestmap, not varchar
                .column(COLUMN_NAME_EMITTED_AT, SQLDataType.TIMESTAMP(6).nullable(false))
                .column(COLUMN_NAME_DATA, structType.nullable(false))
                .getSQL(ParamType.INLINED),
        )
    }

    @Test
    @Throws(Exception::class)
    override fun testCreateTableIncremental() {
        val sql = generator.createTable(incrementalDedupStream, "", false)
        destinationHandler.execute(sql)

        val initialStatuses = destinationHandler.gatherInitialState(listOf(incrementalDedupStream))
        Assertions.assertEquals(1, initialStatuses.size)
        val initialStatus = initialStatuses.first()
        Assertions.assertTrue(initialStatus.isFinalTablePresent)
        Assertions.assertFalse(initialStatus.isSchemaMismatch)
    }

    override fun toJsonValue(valueAsString: String?): Field<*> {
        // mysql lets you just insert json strings directly into json columns
        return DSL.`val`(valueAsString)
    }

    override fun createNamespace(namespace: String) {
        database.execute(
            dslContext
                .createSchemaIfNotExists(nameTransformer.getIdentifier(namespace))
                .getSQL(ParamType.INLINED)
        )
    }

    override fun teardownNamespace(namespace: String) {
        database.execute(
            dslContext
                .dropDatabaseIfExists(nameTransformer.getIdentifier(namespace))
                .getSQL(ParamType.INLINED)
        )
    }

    /**
     * Verify that strings longer than 512 characters survive typing and deduping. MySQL's
     * JSON_VALUE() defaults to VARCHAR(512) and silently returns NULL for longer values. See:
     * https://github.com/airbytehq/airbyte/issues/73303
     */
    @Test
    @Throws(Exception::class)
    fun testLongStringNotTruncated() {
        val longString = "a".repeat(600)

        createRawTable(streamId)
        createFinalTable(incrementalAppendStream, "")
        insertRawTableRecords(
            streamId,
            listOf(
                Jsons.deserialize(
                    """
                    {
                        "_airbyte_raw_id": "ad3e8a20-5328-4b5f-8841-1a1264e5bfc0",
                        "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                        "_airbyte_data": {
                            "id1": 1,
                            "id2": 100,
                            "updated_at": "2023-01-01T01:00:00Z",
                            "string": "$longString"
                        }
                    }
                    """
                )
            ),
        )

        val sql = generator.updateTable(incrementalAppendStream, "", Optional.empty(), false)
        destinationHandler.execute(sql)

        val finalRecords = dumpFinalTableRecords(streamId, "")
        Assertions.assertEquals(1, finalRecords.size, "Expected exactly one final record")
        val stringValue = finalRecords[0].get("string")
        Assertions.assertNotNull(
            stringValue,
            "String field should not be null after typing/deduping"
        )
        Assertions.assertFalse(
            stringValue.isNull,
            "String field should not be JSON null after typing/deduping"
        )
        Assertions.assertEquals(
            longString,
            stringValue.asText(),
            "600-char string should survive typing/deduping without truncation"
        )
    }

    companion object {
        private lateinit var testContainer: MysqlTestDatabase
        private lateinit var database: JdbcDatabase
        private val nameTransformer = MySQLNameTransformer()

        @JvmStatic
        @BeforeAll
        @Throws(Exception::class)
        fun setupMysql() {
            testContainer = MysqlTestDatabase.`in`(MysqlTestDatabase.BaseImage.MYSQL_8)

            val config =
                testContainer
                    .configBuilder()
                    .withDatabase()
                    .withHostAndPort()
                    .withCredentials()
                    .withoutSsl()
                    .build()

            // TODO move this into JdbcSqlGeneratorIntegrationTest?
            // This code was largely copied from RedshiftSqlGeneratorIntegrationTest
            // TODO: Its sad to instantiate unneeded dependency to construct database and
            // datsources. pull it to
            // static methods.
            database =
                DefaultJdbcDatabase(
                    MySQLDestination().getDataSource(config),
                    MysqlTestSourceOperations(),
                )
        }

        @JvmStatic
        @AfterAll
        fun teardownMysql() {
            // Intentionally do nothing.
            // The testcontainer will die at the end of the test run.
        }

        private fun reformatMetaColumnTimestamps(records: List<JsonNode>) {
            // We use mysql's TIMESTAMP(6) type for extracted_at+loaded_at.
            // Unfortunately, mysql doesn't allow you to use the 'Z' suffix for UTC timestamps.
            // Convert those to '+00:00' here.
            for (record in records) {
                reformatTimestampIfPresent(record, COLUMN_NAME_AB_EXTRACTED_AT)
                reformatTimestampIfPresent(record, COLUMN_NAME_EMITTED_AT)
                reformatTimestampIfPresent(record, COLUMN_NAME_AB_LOADED_AT)
            }
        }

        private fun reformatTimestampIfPresent(record: JsonNode, columnNameAbExtractedAt: String) {
            if (record.has(columnNameAbExtractedAt)) {
                val extractedAt = OffsetDateTime.parse(record[columnNameAbExtractedAt].asText())
                val reformattedExtractedAt: String = TIMESTAMP_FORMATTER.format(extractedAt)
                (record as ObjectNode).put(columnNameAbExtractedAt, reformattedExtractedAt)
            }
        }
    }
}
