/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.isDestinationV2
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations
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
        tableName: String?
    ) {
        insertRecordsInternal(
            database,
            records,
            schemaName,
            tableName,
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_META
        )
    }

    @Throws(SQLException::class)
    public override fun insertRecordsInternal(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tmpTableName: String?
    ) {
        insertRecordsInternal(
            database,
            records,
            schemaName,
            tmpTableName,
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
        )
    }

    @Throws(SQLException::class)
    private fun insertRecordsInternal(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tmpTableName: String?,
        vararg columnNames: String
    ) {
        if (records.isEmpty()) {
            return
        }
        // Explicitly passing column order to avoid order mismatches between CREATE TABLE and COPY
        // statement
        val orderedColumnNames = StringUtils.join(columnNames, ", ")
        database.execute { connection: Connection ->
            var tmpFile: File? = null
            try {
                tmpFile = Files.createTempFile("$tmpTableName-", ".tmp").toFile()
                writeBatchToFile(tmpFile, records)

                val copyManager = CopyManager(connection.unwrap(BaseConnection::class.java))
                val sql =
                    String.format(
                        "COPY %s.%s (%s) FROM stdin DELIMITER ',' CSV",
                        schemaName,
                        tmpTableName,
                        orderedColumnNames
                    )
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
    }
}
