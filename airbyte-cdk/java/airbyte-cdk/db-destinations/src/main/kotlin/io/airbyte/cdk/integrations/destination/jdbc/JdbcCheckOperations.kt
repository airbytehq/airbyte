/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.json.Jsons
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.util.*

object JdbcCheckOperations {

    /**
     * Verifies if provided creds has enough permissions. Steps are: 1. Create schema if not exists.
     * 2. Create test table. 3. Insert dummy record to newly created table if "attemptInsert" set to
     * true.
     * 4. Delete table created on step 2.
     *
     * @param outputSchema
     * - schema to tests against.
     * @param database
     * - database to tests against.
     * @param namingResolver
     * - naming resolver.
     * @param sqlOps
     * - SqlOperations object
     * @param attemptInsert
     * - set true if need to make attempt to insert dummy records to newly created table. Set false
     * to skip insert step.
     */
    @JvmStatic
    @Throws(Exception::class)
    fun attemptTableOperations(
        outputSchema: String,
        database: JdbcDatabase,
        namingResolver: NamingConventionTransformer,
        sqlOps: SqlOperations,
        attemptInsert: Boolean
    ) {
        // verify we have write permissions on the target schema by creating a table with a
        // random name,
        // then dropping that table
        try {
            // Get metadata from the database to see whether connection is possible
            database.bufferedResultSetQuery(
                { conn: Connection -> conn.metaData.catalogs },
                { queryContext: ResultSet? ->
                    JdbcUtils.defaultSourceOperations.rowToJson(queryContext!!)
                },
            )

            // verify we have write permissions on the target schema by creating a table with a
            // random name,
            // then dropping that table
            val outputTableName =
                namingResolver.getIdentifier(
                    "_airbyte_connection_test_" +
                        UUID.randomUUID().toString().replace("-".toRegex(), ""),
                )
            sqlOps.createSchemaIfNotExists(database, outputSchema)
            sqlOps.createTableIfNotExists(database, outputSchema, outputTableName)
            // verify if user has permission to make SQL INSERT queries
            try {
                if (attemptInsert) {
                    sqlOps.insertRecords(
                        database,
                        listOf(dummyRecord),
                        outputSchema,
                        outputTableName,
                    )
                }
            } finally {
                sqlOps.dropTableIfExists(database, outputSchema, outputTableName)
            }
        } catch (e: SQLException) {
            if (Objects.isNull(e.cause) || e.cause !is SQLException) {
                throw ConnectionErrorException(e.sqlState, e.errorCode, e.message, e)
            } else {
                val cause = e.cause as SQLException?
                throw ConnectionErrorException(e.sqlState, cause!!.errorCode, cause.message, e)
            }
        } catch (e: Exception) {
            throw Exception(e)
        }
    }

    private val dummyRecord: PartialAirbyteMessage
        /**
         * Generates a dummy AirbyteRecordMessage with random values.
         *
         * @return AirbyteRecordMessage object with dummy values that may be used to test insert
         * permission.
         */
        get() {
            val dummyDataToInsert = Jsons.deserialize("{ \"field1\": true }")
            return PartialAirbyteMessage()
                .withRecord(
                    PartialAirbyteRecordMessage()
                        .withStream("stream1")
                        .withEmittedAt(1602637589000L),
                )
                .withSerialized(dummyDataToInsert.toString())
        }
}
