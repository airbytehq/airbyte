/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.teradata

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation
import io.airbyte.integrations.destination.teradata.util.JSONStruct
import java.sql.SQLException
import java.sql.Timestamp
import java.time.Instant
import java.time.ZoneOffset
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
                ),
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
     * This function queries the database to count the number of records in the `DBC.DatabasesV`
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
                "SELECT COUNT(1) FROM DBC.DatabasesV WHERE DatabaseName = '%s'",
                schemaName,
            ),
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
        schemaName: String?,
        tableName: String?
    ) {
        val tabelCount = checkTableExists(database, schemaName, tableName)
        if (tabelCount == 0) {
            database.execute(
                createTableQuery(database, schemaName, tableName),
            )
        }
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
        val query =
            """SELECT count(1)  FROM DBC.TablesV WHERE TableName = '$tableName'  AND DataBaseName = '$schemaName' """.trimIndent()
        return database?.queryInt(query)
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
        database: JdbcDatabase?,
        schemaName: String?,
        tableName: String?
    ): String {
        return String.format(
            """
        CREATE TABLE %s.%s, FALLBACK  (
          %s VARCHAR(256),
          %s JSON,
          %s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(6),
          %s TIMESTAMP WITH TIME ZONE DEFAULT NULL,
          %s JSON,
          %s BIGINT
          ) UNIQUE PRIMARY INDEX (%s);
        
        """.trimIndent(),
            schemaName,
            tableName,
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_META,
            JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
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
    override fun dropTableIfExists(
        database: JdbcDatabase,
        schemaName: String?,
        tableName: String?
    ) {
        database.execute(dropTableQuery(schemaName, tableName))
    }

    /**
     * Constructs the SQL query for droping a table in the Teradata database.
     *
     * @param schemaName The name of the schema where the table resides.
     * @param tableName The name of the table to be truncated.
     * @return The SQL query string for truncating the table.
     */
    private fun dropTableQuery(schemaName: String?, tableName: String?): String {
        return String.format("DROP TABLE  %s.%s;", schemaName, tableName)
    }

    /**
     * Overwrites given raw table
     *
     * @param database The JdbcDatabase instance to interact with the database.
     * @param rawNamespace The name of the schema where the table resides.
     * @param rawName The name of the table to be dropped.
     */
    override fun overwriteRawTable(database: JdbcDatabase, rawNamespace: String, rawName: String) {
        val tmpName = rawName + AbstractStreamOperation.TMP_TABLE_SUFFIX
        dropTableIfExists(database, rawNamespace, rawName)
        renameTableIfExists(database, rawNamespace, tmpName, rawName)
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
    fun renameTableIfExists(
        database: JdbcDatabase,
        schemaName: String?,
        oldTableName: String?,
        newTableName: String?
    ) {
        database.execute(renameTableQuery(schemaName, oldTableName, newTableName))
    }

    /**
     * Constructs the SQL query for droping a table in the Teradata database.
     *
     * @param schemaName The name of the schema where the table resides.
     * @param tableName The name of the table to be truncated.
     * @return The SQL query string for truncating the table.
     */
    private fun renameTableQuery(
        schemaName: String?,
        oldTableName: String?,
        newTableName: String?
    ): String {
        return String.format(
            "RENAME TABLE  %s.%s TO %s.%s;",
            schemaName,
            oldTableName,
            schemaName,
            newTableName,
        )
    }

    /**
     * Inserts a list of records into a specified table in the Teradata database.
     *
     * @param database The JdbcDatabase instance to interact with the database.
     * @param records The list of AirbyteRecordMessage to be inserted.
     * @param schemaName The name of the schema where the table resides.
     * @param tableName The name of the table where records will be inserted.
     * @throws SQLException If an SQL error occurs during the insert operation.
     */
    public override fun insertRecordsInternalV2(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?,
        syncId: Long,
        generationId: Long
    ) {
        if (records.isEmpty()) {
            return
        }
        val insertQueryComponent =
            java.lang.String.format(
                "INSERT INTO %s.%s (%s, %s, %s, %s, %s) VALUES (?, ?, ?, ?, ?)",
                schemaName,
                tableName,
                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                JavaBaseConstants.COLUMN_NAME_DATA,
                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                JavaBaseConstants.COLUMN_NAME_AB_META,
                JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
            )
        var batchSize = 5000
        if (records.size < 5000) {
            batchSize = records.size
        }
        database.execute { con ->
            try {
                con.prepareStatement(insertQueryComponent).use { stmt ->
                    con.autoCommit = false
                    var batchCount = 0
                    for (record in records) {

                        val uuid = UUID.randomUUID().toString()
                        val jsonData = record.serialized ?: "{}"
                        val meta = record.record?.meta
                        val airbyteMeta =
                            if (meta == null) "{\"changes\":[]}" else Jsons.serialize(meta)

                        var i = 0
                        stmt.setString(++i, uuid)

                        stmt.setObject(
                            ++i,
                            JSONStruct(
                                "JSON",
                                arrayOf(jsonData),
                            ),
                        )
                        val emittedAt = record.record?.emittedAt

                        val extractedAt: Timestamp? =
                            emittedAt?.let {
                                Timestamp.from(
                                    Instant.ofEpochMilli(it).atZone(ZoneOffset.UTC).toInstant()
                                )
                            }
                        stmt.setTimestamp(++i, extractedAt)
                        stmt.setString(++i, airbyteMeta)
                        stmt.setLong(++i, generationId)
                        stmt.addBatch()
                        batchCount++
                        if (batchCount >= batchSize) {
                            stmt.executeBatch()
                            con.commit()
                            batchCount = 0
                        }
                    }
                    if (batchCount > 0) {
                        stmt.executeBatch()
                        con.commit()
                    }
                }
            } catch (e: SQLException) {
                var currentException: SQLException? = e
                while (currentException != null) {
                    LOGGER.error(currentException.message)
                    currentException = currentException.nextException
                }
                throw RuntimeException("Batch insertion failed", e)
            } catch (ex: Exception) {
                LOGGER.error(ex.message)
            } finally {
                con.commit()
            }
        }
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
