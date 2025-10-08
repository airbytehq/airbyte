/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcV1V2Migrator
import java.util.Optional
import lombok.SneakyThrows
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * A migrator class for handling version 1 to version 2 migrations in Teradata. This class extends
 * the `JdbcV1V2Migrator` to provide specific functionality for interacting with Teradata databases
 * during migration processes.
 *
 * @param database The `JdbcDatabase` instance used to interact with the database.
 */
class TeradataV1V2Migrator(database: JdbcDatabase) :
    JdbcV1V2Migrator(StandardNameTransformer(), database, null) {
    /**
     * Retrieves the table definition if it exists in the given namespace and table name.
     *
     * @param namespace The namespace (schema) of the table.
     * @param tableName The name of the table.
     * @return An `Optional` containing the `TableDefinition` if the table exists, or an empty
     * `Optional` if not.
     * @throws Exception If there is an error while fetching the table.
     */
    @SneakyThrows
    @Throws(Exception::class)
    override fun getTableIfExists(
        namespace: String?,
        tableName: String?
    ): Optional<TableDefinition> {
        return JdbcDestinationHandler.Companion.findExistingTable(
            database,
            namespace,
            null,
            tableName
        )
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(
                TeradataV1V2Migrator::class.java,
            )
    }
}
