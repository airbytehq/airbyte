/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.isDestinationV2
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import java.io.File
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.SQLException
import java.sql.Timestamp
import java.time.Instant
import java.util.*
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

abstract class JdbcSqlOperations : SqlOperations {
    protected val schemaSet: MutableSet<String?> = HashSet()

    protected constructor()

    @Throws(Exception::class)
    override fun createSchemaIfNotExists(database: JdbcDatabase?, schemaName: String?) {
        try {
            if (!schemaSet.contains(schemaName) && !isSchemaExists(database, schemaName)) {
                database!!.execute(String.format("CREATE SCHEMA IF NOT EXISTS %s;", schemaName))
                schemaSet.add(schemaName)
            }
        } catch (e: Exception) {
            throw checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    /**
     * When an exception occurs, we may recognize it as an issue with the users permissions or other
     * configuration options. In these cases, we can wrap the exception in a [ConfigErrorException]
     * which will exclude the error from our on-call paging/reporting
     *
     * @param e the exception to check.
     * @return A ConfigErrorException with a message with actionable feedback to the user.
     */
    protected open fun checkForKnownConfigExceptions(
        e: Exception?
    ): Optional<ConfigErrorException> {
        return Optional.empty()
    }

    @Throws(SQLException::class)
    override fun createTableIfNotExists(
        database: JdbcDatabase,
        schemaName: String?,
        tableName: String?
    ) {
        try {
            database.execute(createTableQuery(database, schemaName, tableName))
            for (postCreateSql in postCreateTableQueries(schemaName, tableName)) {
                database.execute(postCreateSql)
            }
        } catch (e: SQLException) {
            throw checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    override fun createTableQuery(
        database: JdbcDatabase?,
        schemaName: String?,
        tableName: String?
    ): String? {
        return if (isDestinationV2) {
            createTableQueryV2(schemaName, tableName)
        } else {
            createTableQueryV1(schemaName, tableName)
        }
    }

    /**
     * Some subclasses may want to execute additional SQL statements after creating the raw table.
     * For example, Postgres does not support index definitions within a CREATE TABLE statement, so
     * we need to run CREATE INDEX statements after creating the table.
     */
    protected open fun postCreateTableQueries(
        schemaName: String?,
        tableName: String?
    ): List<String> {
        return listOf()
    }

    protected open fun createTableQueryV1(schemaName: String?, tableName: String?): String {
        return String.format(
            """
        CREATE TABLE IF NOT EXISTS %s.%s (
          %s VARCHAR PRIMARY KEY,
          %s JSONB,
          %s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        """.trimIndent(),
            schemaName,
            tableName,
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT
        )
    }

    protected open fun createTableQueryV2(schemaName: String?, tableName: String?): String {
        // Note that Meta is the last column in order, there was a time when tables didn't have
        // meta,
        // we issued Alter to add that column so it should be the last column.
        return String.format(
            """
        CREATE TABLE IF NOT EXISTS %s.%s (
          %s VARCHAR PRIMARY KEY,
          %s JSONB,
          %s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
          %s TIMESTAMP WITH TIME ZONE DEFAULT NULL,
          %s JSONB
        );
        
        """.trimIndent(),
            schemaName,
            tableName,
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_META
        )
    }

    // TODO: This method seems to be used by Postgres and others while staging to local temp files.
    // Should there be a Local staging operations equivalent
    @Throws(Exception::class)
    protected fun writeBatchToFile(tmpFile: File?, records: List<PartialAirbyteMessage>) {
        PrintWriter(tmpFile, StandardCharsets.UTF_8).use { writer ->
            CSVPrinter(writer, CSVFormat.DEFAULT).use { csvPrinter ->
                for (record in records) {
                    val uuid = UUID.randomUUID().toString()

                    val jsonData = record.serialized
                    val airbyteMeta =
                        if (record.record!!.meta == null) {
                            "{\"changes\":[]}"
                        } else {
                            Jsons.serialize(record.record!!.meta)
                        }
                    val extractedAt =
                        Timestamp.from(Instant.ofEpochMilli(record.record!!.emittedAt))
                    if (isDestinationV2) {
                        csvPrinter.printRecord(uuid, jsonData, extractedAt, null, airbyteMeta)
                    } else {
                        csvPrinter.printRecord(uuid, jsonData, extractedAt)
                    }
                }
            }
        }
    }

    override fun truncateTableQuery(
        database: JdbcDatabase?,
        schemaName: String?,
        tableName: String?
    ): String {
        return String.format("TRUNCATE TABLE %s.%s;\n", schemaName, tableName)
    }

    override fun insertTableQuery(
        database: JdbcDatabase?,
        schemaName: String?,
        sourceTableName: String?,
        destinationTableName: String?
    ): String? {
        return String.format(
            "INSERT INTO %s.%s SELECT * FROM %s.%s;\n",
            schemaName,
            destinationTableName,
            schemaName,
            sourceTableName
        )
    }

    @Throws(Exception::class)
    override fun executeTransaction(database: JdbcDatabase, queries: List<String>) {
        val appendedQueries = StringBuilder()
        appendedQueries.append("BEGIN;\n")
        for (query in queries) {
            appendedQueries.append(query)
        }
        appendedQueries.append("COMMIT;")
        database.execute(appendedQueries.toString())
    }

    @Throws(SQLException::class)
    override fun dropTableIfExists(
        database: JdbcDatabase,
        schemaName: String?,
        tableName: String?
    ) {
        try {
            database.execute(dropTableIfExistsQuery(schemaName, tableName))
        } catch (e: SQLException) {
            throw checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    fun dropTableIfExistsQuery(schemaName: String?, tableName: String?): String {
        return String.format("DROP TABLE IF EXISTS %s.%s;\n", schemaName, tableName)
    }

    override val isSchemaRequired: Boolean
        get() = true

    override fun isValidData(data: JsonNode?): Boolean {
        return true
    }

    @Throws(Exception::class)
    override fun insertRecords(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    ) {
        if (isDestinationV2) {
            insertRecordsInternalV2(database, records, schemaName, tableName)
        } else {
            insertRecordsInternal(database, records, schemaName, tableName)
        }
    }

    @Throws(Exception::class)
    protected abstract fun insertRecordsInternal(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    )

    @Throws(Exception::class)
    protected abstract fun insertRecordsInternalV2(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    )

    companion object {
        protected const val SHOW_SCHEMAS: String = "show schemas;"
        protected const val NAME: String = "name"
    }
}
