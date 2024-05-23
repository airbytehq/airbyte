/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage

/**
 * SQL queries required for successfully syncing to a destination connector. These operations
 * include the ability to:
 *
 * * Write - insert records from source connector
 * * Create - overloaded function but primarily to create tables if they don't exist (e.g. tmp
 * tables to "stage" records before finalizing to final table
 * * Drop - removes a table from the schema
 * * Insert - move data from one table to another table - usually used for inserting data from tmp
 * to final table (aka airbyte_raw)
 */
interface SqlOperations {
    /**
     * Create a schema with provided name if it does not already exist.
     *
     * @param database Database that the connector is syncing
     * @param schemaName Name of schema.
     * @throws Exception exception
     */
    @Throws(Exception::class)
    fun createSchemaIfNotExists(database: JdbcDatabase?, schemaName: String)

    /**
     * Denotes whether the schema exists in destination database
     *
     * @param database Database that the connector is syncing
     * @param schemaName Name of schema.
     * @return true if the schema exists in destination database, false if it doesn't
     */
    @Throws(Exception::class)
    fun isSchemaExists(database: JdbcDatabase?, schemaName: String?): Boolean {
        return false
    }

    /**
     * Create a table with provided name in provided schema if it does not already exist.
     *
     * @param database Database that the connector is syncing
     * @param schemaName Name of schema
     * @param tableName Name of table
     * @throws Exception exception
     */
    @Throws(Exception::class)
    fun createTableIfNotExists(database: JdbcDatabase, schemaName: String?, tableName: String?)

    /**
     * Query to create a table with provided name in provided schema if it does not already exist.
     *
     * @param database Database that the connector is syncing
     * @param schemaName Name of schema
     * @param tableName Name of table
     * @return query
     */
    fun createTableQuery(database: JdbcDatabase?, schemaName: String?, tableName: String?): String?

    /**
     * Drop the table if it exists.
     *
     * @param schemaName Name of schema
     * @param tableName Name of table
     * @throws Exception exception
     */
    @Throws(Exception::class)
    fun dropTableIfExists(database: JdbcDatabase, schemaName: String?, tableName: String?)

    /**
     * Query to remove all records from a table. Assumes the table exists.
     *
     * @param database Database that the connector is syncing
     * @param schemaName Name of schema
     * @param tableName Name of table
     * @return Query
     */
    fun truncateTableQuery(database: JdbcDatabase?, schemaName: String?, tableName: String?): String

    /**
     * Insert records into table. Assumes the table exists.
     *
     * @param database Database that the connector is syncing
     * @param records Records to insert.
     * @param schemaName Name of schema
     * @param tableName Name of table
     * @throws Exception exception
     */
    @Throws(Exception::class)
    fun insertRecords(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    )

    /**
     * Query to insert all records from source table to destination table. Both tables must be in
     * the specified schema. Assumes both table exist.
     *
     * NOTE: this is an append-only operation meaning that data can be duplicated
     *
     * @param database Database that the connector is syncing
     * @param schemaName Name of schema
     * @param sourceTableName Name of source table
     * @param destinationTableName Name of destination table
     * @return SQL Query string
     */
    fun insertTableQuery(
        database: JdbcDatabase?,
        schemaName: String?,
        sourceTableName: String?,
        destinationTableName: String?
    ): String?

    /**
     * Given an arbitrary number of queries, execute a transaction.
     *
     * @param database Database that the connector is syncing
     * @param queries Queries to execute
     * @throws Exception exception
     */
    @Throws(Exception::class) fun executeTransaction(database: JdbcDatabase, queries: List<String>)

    /** Check if the data record is valid and ok to be written to destination */
    fun isValidData(data: JsonNode?): Boolean

    /**
     * Denotes whether the destination has the concept of schema or not
     *
     * @return true if the destination supports schema (ex: Postgres), false if it doesn't(MySQL)
     */
    val isSchemaRequired: Boolean

    companion object {}
}
