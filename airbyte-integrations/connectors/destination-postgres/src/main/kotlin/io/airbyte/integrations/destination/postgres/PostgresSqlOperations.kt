/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.isDestinationV2
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.BufferedReader
import java.io.File
import java.io.FileReader
import java.io.IOException
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.sql.Connection
import java.sql.SQLException
import org.apache.commons.lang3.StringUtils
import org.postgresql.copy.CopyManager
import org.postgresql.core.BaseConnection

val LOGGER = KotlinLogging.logger {}

class PostgresSqlOperations : JdbcSqlOperations() {
    override fun postCreateTableQueries(schemaName: String?, tableName: String?): List<String> {
        return if (isDestinationV2) {
            java.util.List.of( // the raw_id index _could_ be unique (since raw_id is a UUID)
                // but there's no reason to do that (because it's a UUID :P )
                // and it would just slow down inserts.
                // also, intentionally don't specify the type of index (btree, hash, etc). Just use
                // the default.
                "CREATE INDEX IF NOT EXISTS " +
                    tableName +
                    "_raw_id" +
                    " ON " +
                    schemaName +
                    "." +
                    tableName +
                    "(_airbyte_raw_id)",
                "CREATE INDEX IF NOT EXISTS " +
                    tableName +
                    "_extracted_at" +
                    " ON " +
                    schemaName +
                    "." +
                    tableName +
                    "(_airbyte_extracted_at)",
                "CREATE INDEX IF NOT EXISTS " +
                    tableName +
                    "_loaded_at" +
                    " ON " +
                    schemaName +
                    "." +
                    tableName +
                    "(_airbyte_loaded_at, _airbyte_extracted_at)"
            )
        } else {
            emptyList()
        }
    }

    @Throws(Exception::class)
    override fun insertRecordsInternalV2(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?,
        syncId: Long,
        generationId: Long
    ) {
        insertRecordsInternal(
            database,
            records,
            schemaName,
            tableName,
            syncId,
            generationId,
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_META,
            JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID
        )
    }

    @Throws(SQLException::class)
    private fun insertRecordsInternal(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tmpTableName: String?,
        syncId: Long,
        generationId: Long,
        vararg columnNames: String
    ) {
        if (records.isEmpty()) {
            return
        }
        LOGGER.info { "preparing records to insert. generationId=$generationId, syncId=$syncId" }
        // Explicitly passing column order to avoid order mismatches between CREATE TABLE and COPY
        // statement
        val orderedColumnNames = StringUtils.join(columnNames, ", ")
        database.execute { connection: Connection ->
            var tmpFile: File? = null
            try {
                tmpFile = Files.createTempFile("$tmpTableName-", ".tmp").toFile()
                writeBatchToFile(tmpFile, records, syncId, generationId)

                val copyManager = CopyManager(connection.unwrap(BaseConnection::class.java))
                val sql =
                    String.format(
                        "COPY %s.%s (%s) FROM stdin DELIMITER ',' CSV",
                        schemaName,
                        tmpTableName,
                        orderedColumnNames
                    )
                LOGGER.info { "executing COPY command: $sql" }
                val bufferedReader = BufferedReader(FileReader(tmpFile, StandardCharsets.UTF_8))
                copyManager.copyIn(sql, bufferedReader)
            } catch (e: Exception) {
                throw RuntimeException(e)
            } finally {
                try {
                    if (tmpFile != null) {
                        Files.delete(tmpFile.toPath())
                    }
                } catch (e: IOException) {
                    throw RuntimeException(e)
                }
            }
        }
        LOGGER.info { "COPY command completed sucessfully" }
    }

    override fun overwriteRawTable(database: JdbcDatabase, rawNamespace: String, rawName: String) {
        val tmpName = rawName + AbstractStreamOperation.TMP_TABLE_SUFFIX
        database.executeWithinTransaction(
            listOf(
                "DROP TABLE $rawNamespace.$rawName",
                "ALTER TABLE $rawNamespace.$tmpName RENAME TO $rawName"
            )
        )
    }

    override fun isOtherGenerationIdInTable(
        database: JdbcDatabase,
        generationId: Long,
        namespace: String,
        name: String
    ): Boolean {
        val selectTableResultSet =
            database
                .unsafeQuery(
                    """SELECT 1 
            |               FROM pg_catalog.pg_namespace n
            |               JOIN pg_catalog.pg_class c
            |               ON c.relnamespace=n.oid
            |               WHERE n.nspname=?
            |               AND c.relkind='r'
            |               AND c.relname=?
            |               LIMIT 1
        """.trimMargin(),
                    namespace,
                    name
                )
                .use { it.toList() }
        if (selectTableResultSet.isEmpty()) {
            return false
        } else {
            val selectGenIdResultSet =
                database
                    .unsafeQuery("SELECT _airbyte_generation_id FROM $namespace.$name LIMIT 1;")
                    .use { it.toList() }
            if (selectGenIdResultSet.isEmpty()) {
                return false
            } else {
                val genIdInTable =
                    selectGenIdResultSet.first().get("_airbyte_generation_id")?.asLong()
                LOGGER.info {
                    "found generationId in table $namespace.$name: $genIdInTable (generationId = $generationId)"
                }
                return genIdInTable != generationId
            }
        }
    }
}
