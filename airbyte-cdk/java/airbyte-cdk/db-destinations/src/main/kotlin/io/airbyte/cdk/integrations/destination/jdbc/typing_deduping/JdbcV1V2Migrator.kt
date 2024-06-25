/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.commons.exceptions.SQLRuntimeException
import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import java.sql.DatabaseMetaData
import java.sql.SQLException
import java.util.*

/**
 * Largely based on
 * [io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV1V2Migrator].
 */
open class JdbcV1V2Migrator(
    protected val namingConventionTransformer: NamingConventionTransformer,
    protected val database: JdbcDatabase,
    protected val databaseName: String?
) : BaseDestinationV1V2Migrator<TableDefinition>() {
    override fun doesAirbyteInternalNamespaceExist(streamConfig: StreamConfig?): Boolean {
        val retrievedSchema =
            database.executeMetadataQuery<String> { dbMetadata: DatabaseMetaData ->
                try {
                    dbMetadata.getSchemas(databaseName, streamConfig!!.id.rawNamespace).use {
                        columns ->
                        var schema = ""
                        while (columns.next()) {
                            // Catalog can be null, so don't do anything with it.
                            // columns.getString("TABLE_CATALOG");
                            schema = columns.getString("TABLE_SCHEM")
                        }
                        return@executeMetadataQuery schema
                    }
                } catch (e: SQLException) {
                    throw SQLRuntimeException(e)
                }
            }

        return !retrievedSchema.isEmpty()
    }

    override fun schemaMatchesExpectation(
        existingTable: TableDefinition,
        columns: Collection<String>
    ): Boolean {
        return existingTable.columns.keys.containsAll(columns)
    }

    @Throws(Exception::class)
    override fun getTableIfExists(
        namespace: String?,
        tableName: String?
    ): Optional<TableDefinition> {
        return JdbcDestinationHandler.Companion.findExistingTable(
            database,
            databaseName,
            namespace,
            tableName
        )
    }

    override fun convertToV1RawName(streamConfig: StreamConfig): NamespacedTableName {
        @Suppress("deprecation")
        val tableName = namingConventionTransformer.getRawTableName(streamConfig.id.originalName)
        return NamespacedTableName(
            namingConventionTransformer.getIdentifier(streamConfig.id.originalNamespace),
            tableName
        )
    }
}
