/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator
import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.containsAllIgnoreCase
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import lombok.SneakyThrows
import net.snowflake.client.jdbc.SnowflakeSQLException

private val LOGGER = KotlinLogging.logger {}

@SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
class SnowflakeV1V2Migrator(
    private val namingConventionTransformer: NamingConventionTransformer,
    private val database: JdbcDatabase,
    private val databaseName: String
) : BaseDestinationV1V2Migrator<TableDefinition>() {
    @SneakyThrows
    @Throws(Exception::class)
    override fun doesAirbyteInternalNamespaceExist(streamConfig: StreamConfig?): Boolean {
        try {
            return database
                .queryJsons(
                    "SHOW SCHEMAS LIKE '${streamConfig!!.id.rawNamespace}' IN DATABASE \"$databaseName\";",
                )
                .isNotEmpty()
        } catch (e: SnowflakeSQLException) {
            if (e.message != null && e.message!!.contains("does not exist")) {
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
        return Optional.ofNullable(
            SnowflakeDestinationHandler.getTable(database, namespace!!, tableName!!)
        )
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
