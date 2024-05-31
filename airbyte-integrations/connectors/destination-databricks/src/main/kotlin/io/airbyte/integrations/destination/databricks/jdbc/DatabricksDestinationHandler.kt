/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.jdbc

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType.STRING
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.util.*
import kotlin.streams.asSequence

class DatabricksDestinationHandler(
    private val databaseName: String,
    private val jdbcDatabase: JdbcDatabase,
) : DestinationHandler<MinimumDestinationState.Impl> {

    private val log = KotlinLogging.logger {}
    private val abRawId = DatabricksSqlGenerator.AB_RAW_ID
    private val abExtractedAt = DatabricksSqlGenerator.AB_EXTRACTED_AT
    private val abMeta = DatabricksSqlGenerator.AB_META

    override fun execute(sql: Sql) {
        val transactions: List<List<String>> = sql.transactions
        val queryId = UUID.randomUUID()
        for (transaction in transactions) {
            val transactionId = UUID.randomUUID()
            log.info { "Executing sql $queryId-$transactionId: ${transactions.joinToString("\n")}" }
            val startTime = System.currentTimeMillis()

            try {
                // Databricks DOES NOT support autocommit false. ACID guarantees are within a single
                // table
                // so only MERGE is the supported way if updates/deletes to be done in source &
                // target table.
                // CREATE OR REPLACE...SELECT * from... for swapping a table.
                transaction.forEach { jdbcDatabase.execute(it) }
            } catch (e: SQLException) {
                log.error(e) {
                    "Sql $queryId-$transactionId failed in ${System.currentTimeMillis() - startTime} ms"
                }
                throw e
            }
            log.info {
                "Sql $queryId-$transactionId completed in ${System.currentTimeMillis() - startTime} ms"
            }
        }
    }

    override fun gatherInitialState(
        streamConfigs: List<StreamConfig>
    ): List<DestinationInitialStatus<MinimumDestinationState.Impl>> {
        val streamIds = streamConfigs.stream().map { it.id }.toList()
        val existingTables = findExistingTable(streamIds)
        return streamConfigs
            .stream()
            .asSequence()
            .map {
                val namespace = it.id.finalNamespace
                val name = it.id.finalName
                val initialRawTableStatus =
                    if (it.destinationSyncMode == DestinationSyncMode.OVERWRITE)
                        InitialRawTableStatus(
                            rawTableExists = false,
                            hasUnprocessedRecords = false,
                            maxProcessedTimestamp = Optional.empty(),
                        )
                    else getInitialRawTableState(it.id)
                // finalTablePresent
                if (
                    existingTables.contains(namespace) &&
                        existingTables[namespace]?.contains(name) == true
                ) {
                    DestinationInitialStatus(
                        it,
                        true,
                        initialRawTableStatus,
                        !isSchemaMatch(it, existingTables[namespace]?.get(name)!!),
                        isFinalTableEmpty(it.id),
                        MinimumDestinationState.Impl(false),
                    )
                } else {
                    DestinationInitialStatus(
                        it,
                        false,
                        initialRawTableStatus,
                        isSchemaMismatch = false,
                        isFinalTableEmpty = true,
                        destinationState = MinimumDestinationState.Impl(false),
                    )
                }
            }
            .toList()
    }

    private fun findExistingTable(
        streamIds: List<StreamId>
    ): Map<String, LinkedHashMap<String, TableDefinition>> {
        val paramHolder = IntRange(1, streamIds.size).joinToString { "?" }

        val infoSchemaQuery =
            """
            |SELECT table_schema, table_name, column_name, data_type, is_nullable
            |FROM ${databaseName.lowercase()}.information_schema.columns
            |WHERE 
            |   table_catalog = ?
            |   AND table_schema IN ($paramHolder)
            |   AND table_name IN ($paramHolder)
            |ORDER BY table_schema, table_name, ordinal_position
        """.trimMargin()

        val namespaces = streamIds.asSequence().map { it.finalNamespace }.toList().toTypedArray()
        val names = streamIds.asSequence().map { it.finalName }.toList().toTypedArray()
        val results =
            jdbcDatabase.queryJsons(infoSchemaQuery, databaseName.lowercase(), *namespaces, *names)

        // GroupBys and Associates preserve original iteration order, we used LinkedHashMap in old
        // java land so adapting to it.
        return results
            .groupBy { it.get("table_schema").asText()!! }
            .mapValues { (_, v) ->
                v.groupBy { it.get("table_name").asText()!! }
                    .mapValuesTo(LinkedHashMap()) { (_, v) ->
                        TableDefinition(
                            v.associateTo(LinkedHashMap()) {
                                it.get("column_name").asText()!! to
                                    ColumnDefinition(
                                        it.get("column_name").asText(),
                                        it.get("data_type").asText(),
                                        0,
                                        it.get("is_nullable")
                                            .asText()
                                            .equals("YES", ignoreCase = true),
                                    )
                            },
                        )
                    }
            }
    }

    private fun isSchemaMatch(
        streamConfig: StreamConfig,
        tableDefinition: TableDefinition
    ): Boolean {
        val isAbRawIdMatch =
            tableDefinition.columns.contains(abRawId) &&
                DatabricksSqlGenerator.toDialectType(STRING) ==
                    tableDefinition.columns[abRawId]?.type
        val isAbExtractedAtMatch =
            tableDefinition.columns.contains(abExtractedAt) &&
                DatabricksSqlGenerator.toDialectType(TIMESTAMP_WITH_TIMEZONE) ==
                    tableDefinition.columns[abExtractedAt]?.type
        val isAbMetaMatch =
            tableDefinition.columns.contains(abMeta) &&
                DatabricksSqlGenerator.toDialectType(STRING) ==
                    tableDefinition.columns[abMeta]?.type
        if (!isAbRawIdMatch || !isAbExtractedAtMatch || !isAbMetaMatch) return false

        val expectedColumns =
            streamConfig.columns.entries.associate {
                it.key.name to DatabricksSqlGenerator.toDialectType(it.value)
            }
        val actualColumns =
            tableDefinition.columns.entries
                .filter { (it.key != abRawId && it.key != abExtractedAt && it.key != abMeta) }
                .associate {
                    it.key!! to if (it.value.type != "DECIMAL") it.value.type else "DECIMAL(38, 10)"
                }
        return actualColumns == expectedColumns
    }

    private fun isFinalTableEmpty(id: StreamId): Boolean {
        return !jdbcDatabase.queryBoolean(
            "SELECT EXISTS (SELECT 1 from $databaseName.${
                id.finalTableId(
                    DatabricksSqlGenerator.QUOTE,
                )
            });",
        )
    }

    private fun findLastLoadedTs(query: String): Optional<Instant> {
        return jdbcDatabase
            .bufferedResultSetQuery(
                { connection: Connection -> connection.createStatement().executeQuery(query) },
                { resultSet: ResultSet ->
                    resultSet.getObject("last_loaded_at", LocalDateTime::class.java)
                },
            )
            .stream()
            .filter { ts: LocalDateTime? -> Objects.nonNull(ts) }
            .findFirst()
            .map {
                // Databricks doesn't have offset stored, so we always use UTC as the supposed
                // timezone
                it.toInstant(ZoneOffset.UTC)
            }
    }

    private fun getInitialRawTableState(id: StreamId): InitialRawTableStatus {
        jdbcDatabase
            .executeMetadataQuery { metadata ->
                // Handle resultset call in the function which will be closed
                // after the scope is exited
                val resultSet =
                    metadata?.getTables(
                        databaseName,
                        id.rawNamespace,
                        id.rawName,
                        null,
                    )
                resultSet?.next() ?: false
            }
            .let {
                if (!it) {
                    return InitialRawTableStatus(
                        rawTableExists = false,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.empty(),
                    )
                }
            }

        val minExtractedAtLoadedNotNullQuery =
            """
            |SELECT min(`${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT}`) as last_loaded_at
            |FROM $databaseName.${id.rawTableId(DatabricksSqlGenerator.QUOTE)}
            |WHERE ${JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT} IS NULL
            |""".trimMargin()
        val maxExtractedAtQuery =
            """
            |SELECT max(`${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT}`) as last_loaded_at
            |FROM $databaseName.${id.rawTableId(DatabricksSqlGenerator.QUOTE)}
        """.trimMargin()

        findLastLoadedTs(minExtractedAtLoadedNotNullQuery)
            .map { it.minusSeconds(1) }
            .let {
                if (it.isPresent)
                    return InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = true,
                        maxProcessedTimestamp = it,
                    )
            }
        findLastLoadedTs(maxExtractedAtQuery).let {
            return InitialRawTableStatus(
                rawTableExists = true,
                hasUnprocessedRecords = false,
                maxProcessedTimestamp = it,
            )
        }
    }

    override fun commitDestinationStates(
        destinationStates: Map<StreamId, MinimumDestinationState.Impl>
    ) {
        // do Nothing
    }
}
