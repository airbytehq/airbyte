/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator
import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.containsAllIgnoreCase
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabaseUtils.changeDataTypeFromShowQuery
import java.util.*
import lombok.SneakyThrows
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
class SnowflakeV1V2Migrator(
    private val namingConventionTransformer: NamingConventionTransformer,
    private val database: JdbcDatabase,
    private val databaseName: String
) : BaseDestinationV1V2Migrator<TableDefinition>() {

    private val LOGGER: Logger =
        LoggerFactory.getLogger(SnowflakeV1V2Migrator::class.java)

    @SneakyThrows
    @Throws(Exception::class)
    override fun doesAirbyteInternalNamespaceExist(streamConfig: StreamConfig?): Boolean {

        try {
            val showSchemaQuery =
                """
                SHOW SCHEMAS LIKE '${streamConfig!!.id.rawNamespace}' IN DATABASE "$databaseName";
                """.trimIndent()
            val showSchemaResult = database.queryJsons(
                                    showSchemaQuery,
                                )
            return showSchemaResult.isNotEmpty()
        } catch (e: SnowflakeSQLException) {
            if(e.message != null && e.message!!.contains("does not exist")) {
                return false
            } else {
                throw e
            }
        }
    }

    override fun schemaMatchesExpectation(
        existingTable: TableDefinition,
        columns: Collection<String>
    ): Boolean {
        return containsAllIgnoreCase(existingTable.columns.keys, columns)
    }

    @SneakyThrows
    @Throws(Exception::class)
    override fun getTableIfExists(
        namespace: String?,
        tableName: String?
    ): Optional<TableDefinition> {
        // TODO this looks similar to SnowflakeDestinationHandler#findExistingTables, with a twist;
        // databaseName not upper-cased and rawNamespace and rawTableName as-is (no uppercase).
        // The obvious database.getMetaData().getColumns() solution doesn't work, because JDBC
        // translates
        // VARIANT as VARCHAR

        try {
            val showColumnsQuery =
                    """
                       SHOW COLUMNS IN TABLE "$databaseName"."$namespace"."$tableName";
                    """.trimIndent()
            val showColumnsResult = database.queryJsons(
                showColumnsQuery
            )
            val columnsFromShowQuery = showColumnsResult
                .stream()
                .collect(
                    { LinkedHashMap() },
                    { map: java.util.LinkedHashMap<String, ColumnDefinition>, row: JsonNode ->
                        map[row["column_name"].asText()] =
                            ColumnDefinition(
                                row["column_name"].asText(),
                                changeDataTypeFromShowQuery(ObjectMapper().readTree(row["data_type"].asText()).path("type").asText()),
                                0,
                                row["null?"].asText().toBoolean(),
                            )
                    },
                    { obj: java.util.LinkedHashMap<String, ColumnDefinition>,
                      m: java.util.LinkedHashMap<String, ColumnDefinition>? ->
                        obj.putAll(m!!)
                    },
                )
            return if (columnsFromShowQuery.isEmpty()) {
                Optional.empty()
            } else {
                Optional.of(TableDefinition(columnsFromShowQuery))
            }
        } catch (e: SnowflakeSQLException) {
            if(e.message != null && e.message!!.contains("does not exist")) {
                return Optional.empty()
            } else {
                throw e
            }
        }
    }

    override fun convertToV1RawName(streamConfig: StreamConfig): NamespacedTableName {
        // The implicit upper-casing happens for this in the SqlGenerator
        @Suppress("deprecation")
        val tableName = namingConventionTransformer.getRawTableName(streamConfig.id.originalName)
        return NamespacedTableName(
            namingConventionTransformer.getIdentifier(streamConfig.id.originalNamespace),
            tableName
        )
    }

    @Throws(Exception::class)
    override fun doesValidV1RawTableExist(namespace: String?, tableName: String?): Boolean {
        // Previously we were not quoting table names and they were being implicitly upper-cased.
        // In v2 we preserve cases
        return super.doesValidV1RawTableExist(
            namespace!!.uppercase(Locale.getDefault()),
            tableName!!.uppercase(Locale.getDefault())
        )
    }
}
