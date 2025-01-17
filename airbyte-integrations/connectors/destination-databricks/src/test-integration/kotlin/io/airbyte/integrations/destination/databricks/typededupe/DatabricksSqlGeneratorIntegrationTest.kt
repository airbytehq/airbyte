/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.typededupe

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.DatabricksConnectorClientsFactory
import io.airbyte.integrations.destination.databricks.DatabricksIntegrationTestUtils
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksNamingTransformer
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import java.sql.Connection
import java.sql.ResultSet
import java.util.Optional
import java.util.concurrent.TimeUnit
import kotlin.streams.asSequence
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.mockito.Mockito.mock

class DatabricksSqlGeneratorIntegrationTest :
    BaseSqlGeneratorIntegrationTest<MinimumDestinationState.Impl>() {
    companion object {
        private var jdbcDatabase: JdbcDatabase = mock()
        private var connectorConfig: DatabricksConnectorConfig = mock()
        @JvmStatic
        @BeforeAll
        @Timeout(value = 10, unit = TimeUnit.MINUTES)
        fun setupDatabase() {
            connectorConfig = DatabricksIntegrationTestUtils.oauthConfig
            jdbcDatabase =
                DefaultJdbcDatabase(
                    DatabricksConnectorClientsFactory.createDataSource(connectorConfig)
                )
            // This will trigger warehouse start
            jdbcDatabase.execute("SELECT 1")
        }
    }

    override val sqlGenerator: SqlGenerator
        get() = 
            DatabricksSqlGenerator(DatabricksNamingTransformer(), connectorConfig.database, false)
    private val databricksSqlGenerator = sqlGenerator as DatabricksSqlGenerator
    override val destinationHandler: DestinationHandler<MinimumDestinationState.Impl>
        get() =
            DatabricksDestinationHandler(
                databricksSqlGenerator,
                connectorConfig.database,
                jdbcDatabase,
            )
    override val supportsSafeCast: Boolean
        get() = true

    override fun createNamespace(namespace: String) {
        destinationHandler.execute(sqlGenerator.createSchema(namespace))
    }

    override fun createRawTable(streamId: StreamId) {
        destinationHandler.execute(
            databricksSqlGenerator.createRawTable(
                streamId,
                suffix = "",
                replace = false,
            ),
        )
    }

    override fun createV1RawTable(v1RawTable: StreamId) {
        throw NotImplementedError("Databricks does not support a V1->V2 migration")
    }

    override fun insertRawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        val columnNames =
            listOf(
                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                JavaBaseConstants.COLUMN_NAME_DATA,
                JavaBaseConstants.COLUMN_NAME_AB_META,
                JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
            )
        val tableIdentifier = streamId.rawTableId(DatabricksSqlGenerator.QUOTE)
        insertRecords(columnNames, tableIdentifier, records)
        //        // Exercise using the original inserts code path
        //        val ops =
        //            DatabricksStorageOperations(
        //                sqlGenerator,
        //                destinationHandler,
        //                ConnectorClientsFactory.createWorkspaceClient(
        //                    connectorConfig.hostname,
        //                    connectorConfig.apiAuthentication,
        //                ),
        //                connectorConfig.database,
        //            )
        //        ops.prepareStagingVolume(incrementalDedupStream.id)
        //        val streamOps = DatabricksStreamOperations(ops, FileUploadFormat.CSV)
        //        val transformedRecords: Stream<PartialAirbyteMessage> =
        //            records.stream().map {
        //                PartialAirbyteMessage()
        //                    .withSerialized(Jsons.serialize(it.get("_airbyte_data")))
        //                    .withRecord(
        //                        PartialAirbyteRecordMessage()
        //                            .withEmittedAt(
        //                                ZonedDateTime.parse(
        //                                    it.get("_airbyte_extracted_at").asText(),
        //                                    DateTimeFormatter.ISO_ZONED_DATE_TIME,
        //                                )
        //                                    .toInstant()
        //                                    .toEpochMilli(),
        //                            ),
        //                    )
        //            }
        //        streamOps.writeRecords(incrementalDedupStream, transformedRecords)
    }

    override fun insertV1RawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        throw NotImplementedError("Databricks does not support a V1->V2 migration")
    }

    override fun insertFinalTableRecords(
        includeCdcDeletedAt: Boolean,
        streamId: StreamId,
        suffix: String?,
        records: List<JsonNode>,
        generationId: Long,
    ) {
        val columnNames =
            if (includeCdcDeletedAt) FINAL_TABLE_COLUMN_NAMES_CDC else FINAL_TABLE_COLUMN_NAMES
        val tableIdentifier =
            streamId.finalTableId(DatabricksSqlGenerator.QUOTE, suffix?.lowercase() ?: "")
        insertRecords(
            columnNames,
            tableIdentifier,
            records.map {
                (it as ObjectNode).put(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, generationId)
            },
        )
    }

    private fun insertRecords(
        columnNames: List<String>,
        tableIdentifier: String,
        records: List<JsonNode>
    ) {
        val sqlValue = { value: JsonNode? ->
            value?.let {
                if (value.isTextual) "'${value.asText()}'"
                else if (value.isNumber) "$value"
                else "\"${value.toString().replace("\\", "\\\\").replace("\"", "\\\"")}\""
            }
                ?: "NULL"
        }
        val columnStr = columnNames.joinToString { "`$it`" }
        val colNumberStr = IntRange(1, columnNames.size).joinToString { "`col$it`" }
        val values =
            records
                .stream()
                .asSequence()
                .map { json ->
                    columnNames
                        .stream()
                        .asSequence()
                        .map { json.get(it) }
                        .map(sqlValue)
                        .joinToString(prefix = "(", postfix = ")")
                }
                .joinToString(", \n")
        val insertRecordsSql =
            """
            | INSERT INTO ${connectorConfig.database}.$tableIdentifier (
            | $columnStr
            | )
            | SELECT
            | $colNumberStr
            | FROM 
            | VALUES
            |${values.replaceIndent("   ")}
        """.trimMargin()
        println(insertRecordsSql)
        jdbcDatabase.execute(insertRecordsSql)
    }

    override fun dumpRawTableRecords(streamId: StreamId): List<JsonNode> {
        return dumpTable(streamId.rawTableId(DatabricksSqlGenerator.QUOTE))
    }

    override fun dumpFinalTableRecords(streamId: StreamId, suffix: String?): List<JsonNode> {
        return dumpTable(streamId.finalTableId(DatabricksSqlGenerator.QUOTE, suffix ?: ""))
    }

    override fun teardownNamespace(namespace: String) {
        jdbcDatabase.execute(
            "DROP SCHEMA IF EXISTS ${connectorConfig.database}.${namespace.lowercase()} CASCADE"
        )
        //        println("Skipping teardown for now, re-enable $namespace")
    }

    private fun dumpTable(tableIdentifier: String): List<JsonNode> {
        val sourceOperations =
            object : JdbcSourceOperations() {
                override fun copyToJsonField(
                    resultSet: ResultSet,
                    colIndex: Int,
                    json: ObjectNode
                ) {
                    // TODO: This is a hack looking at columnName to determine
                    //  which complex types are mapped to String. derive it from airbyteType
                    val columnName = resultSet.metaData.getColumnName(colIndex)
                    if (
                        columnName == "unknown" ||
                            columnName == "struct" ||
                            columnName == "array" ||
                            columnName == "_airbyte_meta"
                    ) {
                        json.set<JsonNode>(
                            columnName,
                            Jsons.deserializeExact(resultSet.getString(colIndex)),
                        )
                        return
                    }
                    super.copyToJsonField(resultSet, colIndex, json)
                }
            }
        return jdbcDatabase.bufferedResultSetQuery<JsonNode>(
            { connection: Connection ->
                connection
                    .createStatement()
                    .executeQuery(
                        """
                        SELECT *
                        FROM ${connectorConfig.database}.$tableIdentifier 
                        ORDER BY ${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT} ASC
                    """.trimIndent(),
                    )
            },
            { resultSet: ResultSet ->
                sourceOperations.rowToJson(
                    resultSet,
                )
            },
        )
    }

    @Disabled override fun testCreateTableIncremental() {}

    @Disabled("No V1 Table migration for databricks") override fun testV1V2migration() {}

    @Disabled("No state table in databricks")
    override fun testStateHandling() {
        super.testStateHandling()
    }
    @Timeout(value = 5, unit = TimeUnit.MINUTES)
    @Test
    @Disabled
    fun randomTest() {
        // createRawTable(incrementalDedupStream.id)
        createFinalTable(incrementalDedupStream, "")
        //        val sql = sqlGenerator.createTable(incrementalDedupStream, "", true)
        //        val ops = DatabricksStorageOperations(
        //            sqlGenerator,
        //            destinationHandler,
        //            ConnectorClientsFactory.createWorkspaceClient(
        //                connectorConfig.hostname,
        //                connectorConfig.apiAuthentication,
        //            ),
        //            connectorConfig.database,
        //        )
        //        ops.prepareStagingVolume(incrementalDedupStream.id)
        //        val streamOps = DatabricksStreamOperations(ops, FileUploadFormat.CSV)
        //        var records: Stream<PartialAirbyteMessage> =
        //            BaseTypingDedupingTest.readRecords("sqlgenerator/alltypes_inputrecords.jsonl")
        //                .stream()
        //                .map {
        //                    PartialAirbyteMessage()
        //                        .withSerialized(Jsons.serialize(it.get("_airbyte_data")))
        //                        .withRecord(
        //                            PartialAirbyteRecordMessage()
        //                                .withEmittedAt(ZonedDateTime
        //                                    .parse(it.get("_airbyte_extracted_at").asText(),
        // DateTimeFormatter.ISO_ZONED_DATE_TIME)
        //                                    .toInstant()
        //                                    .toEpochMilli()))
        //                }
        //        streamOps.writeRecords(incrementalDedupStream, records)
        //        records =
        // BaseTypingDedupingTest.readRecords("sqlgenerator/alltypes_inputrecords.jsonl")
        //            .stream()
        //            .map {
        //                PartialAirbyteMessage()
        //                    .withSerialized(Jsons.serialize(it.get("_airbyte_data")))
        //                    .withRecord(
        //                        PartialAirbyteRecordMessage()
        //                            .withEmittedAt(
        //                                ZonedDateTime
        //                                    .parse(
        //                                        it.get("_airbyte_extracted_at").asText(),
        //                                        DateTimeFormatter.ISO_ZONED_DATE_TIME,
        //                                    )
        //                                    .toInstant()
        //                                    .toEpochMilli(),
        //                            ),
        //                    )
        //            }
        //        streamOps.writeRecords(incrementalDedupStream, records)
        //        println(sql)
        //        println(sqlGenerator.updateTable(cdcIncrementalDedupStream, "", Optional.empty(),
        // false).transactions.first().first())
        /*insertFinalTableRecords(
            true,
            cdcIncrementalDedupStream.id,
            "",
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/cdcupdate_inputrecords_final.jsonl",
            ),
        )*/
        // println(dumpFinalTableRecords(cdcIncrementalDedupStream.id, ""))
        val columns = LinkedHashMap<ColumnId, AirbyteType>()
        val id1 = sqlGenerator.buildColumnId("id1")
        val id2 = sqlGenerator.buildColumnId("id2")
        columns[id1] = AirbyteProtocolType.INTEGER
        columns[id2] = AirbyteProtocolType.INTEGER
        columns[generator.buildColumnId("struct")] = Struct(LinkedHashMap())
        columns[generator.buildColumnId("array")] = Array(AirbyteProtocolType.UNKNOWN)
        columns[generator.buildColumnId("string")] = AirbyteProtocolType.STRING
        columns[generator.buildColumnId("number")] = AirbyteProtocolType.NUMBER
        columns[generator.buildColumnId("integer")] = AirbyteProtocolType.INTEGER
        columns[generator.buildColumnId("boolean")] = AirbyteProtocolType.BOOLEAN
        columns[generator.buildColumnId("timestamp_with_timezone")] =
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
        columns[generator.buildColumnId("timestamp_without_timezone")] =
            AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE
        columns[generator.buildColumnId("time_with_timezone")] =
            AirbyteProtocolType.TIME_WITH_TIMEZONE
        columns[generator.buildColumnId("time_without_timezone")] =
            AirbyteProtocolType.TIME_WITHOUT_TIMEZONE
        val tmpStream =
            StreamConfig(
                buildStreamId("sql_generator_test_svcnfgcqaz", "users_final", "users_raw"),
                ImportType.DEDUPE,
                listOf(),
                Optional.empty(),
                columns,
                0,
                0,
                0
            )
        val initialStates =
            destinationHandler.gatherInitialState(listOf(incrementalDedupStream, tmpStream))
        initialStates.forEach {
            println("==========================")
            println(it.streamConfig.id)
            println(it.isSchemaMismatch)
            println(it.isFinalTablePresent)
            println(it.isFinalTableEmpty)
            println(it.initialRawTableStatus)
        }
    }

    @Disabled(
        "Create schema and table doesn't use the actual truncation handling, uses test method"
    )
    override fun testLongIdentifierHandling() {
        super.testLongIdentifierHandling()
    }

    // Failing tests
    // weirdColumnNames - double-quote is removed, as it cannot be queried
    // testLongIdentifierHandling - Ignored
}
