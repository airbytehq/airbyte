/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.destination.teradata.util.JSONStruct
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.sql.Connection
import java.sql.SQLException
import java.sql.Timestamp
import java.time.Instant
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * The TeradataSqlOperations class is responsible for performing SQL operations on the Teradata
 * database. It extends the JdbcSqlOperations class to provide functionalities specific to the
 * Teradata integration, including inserting records, creating schemas and tables, and executing SQL
 * transactions.
 */
class TeradataSqlOperations : JdbcSqlOperations() {

    /**
     * Inserts a list of records into a specified table in the Teradata database.
     *
     * @param database The JdbcDatabase instance to interact with the database.
     * @param records The list of AirbyteRecordMessage to be inserted.
     * @param schemaName The name of the schema where the table resides.
     * @param tableName The name of the table where records will be inserted.
     * @throws SQLException If an SQL error occurs during the insert operation.
     */
    @Throws(SQLException::class)
    override fun insertRecordsInternal(
        database: JdbcDatabase,
        records: List<AirbyteRecordMessage>,
        schemaName: String,
        tableName: String
    ) {
        if (records.isEmpty()) {
            return
        }
        val insertQueryComponent =
            String.format(
                "INSERT INTO %s.%s (%s, %s, %s) VALUES (?, ?, ?)",
                schemaName,
                tableName,
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_DATA,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            )
        database.execute { con: Connection ->
            con.prepareStatement(insertQueryComponent).use { stmt ->
                for (record in records) {
                    val uuid = UUID.randomUUID().toString()
                    val jsonData = Jsons.serialize(formatData(record.data))
                    val emittedAt = Timestamp.from(Instant.ofEpochMilli(record.emittedAt))

                    stmt.setString(1, uuid)
                    stmt.setObject(2, JSONStruct("JSON", arrayOf(jsonData)))
                    stmt.setTimestamp(3, emittedAt)
                    stmt.addBatch()
                }
                stmt.executeBatch()
            }
        }
    }

    /**
     * Creates a schema in the Teradata database if it does not already exist.
     *
     * @param database The JdbcDatabase instance to interact with the database.
     * @param schemaName The name of the schema to be created.
     * @throws Exception If an error occurs while creating the schema.
     */
    @Throws(Exception::class)
    override fun createSchemaIfNotExists(database: JdbcDatabase?, schemaName: String) {
        if (!isSchemaExists(database, schemaName)) {
            database?.execute(
                String.format(
                    "CREATE DATABASE \"%s\" AS PERMANENT = 120e6, SPOOL = 120e6;",
                    schemaName,
                )
            )
        } else {
            LOGGER.warn(
                "Database $schemaName already exists.",
            )
        }
    }

    /**
     * Checks if a schema with the specified name exists in the given database.
     *
     * This function queries the database to count the number of records in the `DBC.Databases`
     * table that match the provided `schemaName`. If the count is greater than 0, the function
     * returns `true`, indicating that the schema exists. Otherwise, it returns `false`.
     *
     * @param database The database object to query.
     * @param schemaName The name of the schema to check for existence.
     * @return `true` if the schema exists in the database, `false` otherwise. Returns `false` if
     * the database or schema name is `null`.
     */
    @Throws(Exception::class)
    override fun isSchemaExists(database: JdbcDatabase?, schemaName: String?): Boolean {
        return (database?.queryInt(
            String.format(
                "SELECT COUNT(1) FROM DBC.Databases WHERE DatabaseName = '%s'",
                schemaName,
            )
        )
            ?: 0) > 0 // If the result is greater than 0, return true, else false
    }
    /**
     * Creates a table in the Teradata database if it does not already exist.
     *
     * @param database The JdbcDatabase instance to interact with the database.
     * @param schemaName The name of the schema where the table resides.
     * @param tableName The name of the table to be created.
     * @throws SQLException If an SQL error occurs during the creation of the table.
     */
    @Throws(SQLException::class)
    override fun createTableIfNotExists(
        database: JdbcDatabase,
        schemaName: String,
        tableName: String
    ) {
        if (checkTableExists(database, schemaName, tableName) == 0)
            database.execute(createTableQuery(database, schemaName, tableName))
    }
    /**
     * Checks whether a table with the given name exists in the specified schema of the database.
     *
     * This method queries the database to determine if a table exists in the specified schema. It
     * returns a value greater than 0 if the table exists, and 0 if the table does not exist.
     *
     * @param database The database instance where the table check is performed.
     * @param schemaName The name of the schema in which to check for the table. Can be `null` if no
     * schema is used.
     * @param tableName The name of the table to check for. Must not be `null`.
     *
     * @return A positive integer if the table exists, otherwise 0 if the table does not exist.
     *
     * @throws SQLException If an SQL error occurs while checking for the table's existence.
     */
    @Throws(SQLException::class)
    private fun checkTableExists(
        database: JdbcDatabase?,
        schemaName: String?,
        tableName: String?
    ): Int? {
        return database?.queryInt(
            String.format(
                "SELECT COUNT(1) FROM DBC.TABLES WHERE DatabaseName = '%s' AND TableName = '%s' AND TableKind = 'T'",
                schemaName,
                tableName
            )
        )
    }
    /**
     * Constructs the SQL query for creating a new table in the Teradata database.
     *
     * @param database The JdbcDatabase instance to interact with the database.
     * @param schemaName The name of the schema where the table will be created.
     * @param tableName The name of the table to be created.
     * @return The SQL query string for creating the table.
     */
    override fun createTableQuery(
        database: JdbcDatabase,
        schemaName: String,
        tableName: String
    ): String {
        return String.format(
            "CREATE SET TABLE %s.%s, FALLBACK ( %s VARCHAR(256), %s JSON, %s TIMESTAMP(6)) " +
                " UNIQUE PRIMARY INDEX (%s) ",
            schemaName,
            tableName,
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_ID,
        )
    }
    /**
     * Drops a specified table from the Teradata database if it exists.
     *
     * @param database The JdbcDatabase instance to interact with the database.
     * @param schemaName The name of the schema where the table resides.
     * @param tableName The name of the table to be dropped.
     * @throws SQLException If an SQL error occurs during the drop operation.
     */
    @Throws(SQLException::class)
    override fun dropTableIfExists(database: JdbcDatabase, schemaName: String, tableName: String) {
        database.execute(dropTableIfExistsQueryInternal(schemaName, tableName))
    }
    /**
     * Constructs the SQL query for truncating a table in the Teradata database.
     *
     * @param database The JdbcDatabase instance to interact with the database.
     * @param schemaName The name of the schema where the table resides.
     * @param tableName The name of the table to be truncated.
     * @return The SQL query string for truncating the table.
     */
    override fun truncateTableQuery(
        database: JdbcDatabase,
        schemaName: String,
        tableName: String
    ): String {
        return String.format("DELETE %s.%s ALL;\n", schemaName, tableName)
    }

    private fun dropTableIfExistsQueryInternal(schemaName: String, tableName: String): String {
        return String.format("DROP TABLE %s.%s;\n", schemaName, tableName)
    }
    /**
     * Executes a list of SQL queries as a single transaction.
     *
     * @param database The JdbcDatabase instance to interact with the database.
     * @param queries The list of SQL queries to be executed.
     * @throws Exception If an error occurs during the transaction execution.
     */
    @Throws(Exception::class)
    override fun executeTransaction(database: JdbcDatabase, queries: List<String>) {
        val appendedQueries = StringBuilder()
        if (queries.isNotEmpty()) {
            for (query in queries) {
                appendedQueries.append(query)
            }
            database.execute(appendedQueries.toString())
        }
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(
                TeradataSqlOperations::class.java,
            )
    }
}
