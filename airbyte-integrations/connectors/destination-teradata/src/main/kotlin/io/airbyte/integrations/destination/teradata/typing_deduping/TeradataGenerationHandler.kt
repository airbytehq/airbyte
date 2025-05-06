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
        val result = isTableExists(database, namespace, name)
        if (result) {
            val columnExists =
                database
                    .unsafeQuery(
                        "SELECT ColumnName FROM dbc.columnsv WHERE DatabaseName = '$namespace' AND TableName = '$name' AND ColumnName = '_airbyte_generation_id';"
                    )
                    .use { it.toList() }
            if (columnExists.isEmpty()) {
                LOGGER.warn(
                    "Column $namespace.$name._airbyte_generation_id does not exist in $namespace.$name."
                )
                return null
            }
            val selectGenIdResultSet =
                database
                    .unsafeQuery("SELECT max(_airbyte_generation_id) FROM $namespace.$name;")
                    .use { it.toList() }
            if (selectGenIdResultSet.isEmpty()) {
                return null
            } else {
                val genIdInTable =
                    selectGenIdResultSet.first().get("_airbyte_generation_id")?.asLong()
                return genIdInTable ?: -1L
            }
        } else LOGGER.warn("Table $namespace.$name does not exist in the database.")
        return null
    }

    /**
     * Checks whether a table with the given name exists in the specified schema of the database.
     *
     * This method queries the database to determine if a table exists in the specified schema. It
     * returns true if the table exists, and false if the table does not exist.
     *
     * @param jdbcDatabase The database instance where the table check is performed.
     * @param schemaName The name of the schema in which to check for the table. Can be `null` if no
     * schema is used.
     * @param tableName The name of the table to check for. Must not be `null`.
     *
     * @return true if the table exists, otherwise false if the table does not exist.
     */
    private fun isTableExists(
        jdbcDatabase: JdbcDatabase,
        schemaName: String?,
        tableName: String?
    ): Boolean {
        val countQuery =
            """SELECT count(1)  FROM DBC.TablesV WHERE TableName = '$tableName'  AND DataBaseName = '$schemaName' """.trimIndent()
        return jdbcDatabase.queryInt(countQuery) >
            0 // If the result is greater than 0, return true, else false
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(TeradataGenerationHandler::class.java)
    }
}
