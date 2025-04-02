/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.JdbcGenerationHandler
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * A class responsible for handling Teradata-specific generation operations. This class implements
 * the `JdbcGenerationHandler` interface and provides methods for interacting with the generation id
 * within Teradata tables.
 *
 * @constructor Initializes a new instance of `TeradataGenerationHandler`.
 */
class TeradataGenerationHandler() : JdbcGenerationHandler {
    /**
     * Retrieves the generation ID from a Teradata table.
     *
     * @param database The `JdbcDatabase` instance used to interact with the database.
     * @param namespace The namespace (schema) of the table.
     * @param name The name of the table.
     * @return A `Long?` representing the generation ID in the table, or `null` if no generation ID
     * is found.
     */
    override fun getGenerationIdInTable(
        database: JdbcDatabase,
        namespace: String,
        name: String
    ): Long? {
        val columnExists =
            database
                .unsafeQuery(
                    "SELECT ColumnName FROM dbc.columns WHERE DatabaseName = '$namespace' AND TableName = '$name' AND ColumnName = '_airbyte_generation_id';"
                )
                .use { it.toList() }
        if (columnExists.isEmpty()) {
            LOGGER.warn("Column _airbyte_generation_id does not exist in table $namespace.$name")
            return null
        }
        val selectGenIdResultSet =
            database.unsafeQuery("SELECT max(_airbyte_generation_id) FROM $namespace.$name;").use {
                it.toList()
            }
        if (selectGenIdResultSet.isEmpty()) {
            return null
        } else {
            val genIdInTable = selectGenIdResultSet.first().get("_airbyte_generation_id")?.asLong()
            return genIdInTable ?: -1L
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(TeradataGenerationHandler::class.java)
    }
}
