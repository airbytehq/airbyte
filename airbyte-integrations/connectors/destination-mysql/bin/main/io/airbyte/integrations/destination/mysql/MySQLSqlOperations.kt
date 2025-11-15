/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations
import java.io.File
import java.io.IOException
import java.nio.file.Files
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.util.stream.Collectors
import java.util.stream.IntStream
import org.jooq.SQLDialect
import org.jooq.impl.DSL

@SuppressFBWarnings(
    value = ["SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE"],
    justification =
        "There is little chance of SQL injection. There is also little need for statement reuse. The basic statement is more readable than the prepared statement."
)
class MySQLSqlOperations : JdbcSqlOperations() {
    private var isLocalFileEnabled = false

    @Throws(Exception::class)
    override fun executeTransaction(database: JdbcDatabase, queries: List<String>) {
        database.executeWithinTransaction(queries)
    }

    @Throws(SQLException::class)
    public override fun insertRecordsInternal(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tmpTableName: String?
    ) {
        throw UnsupportedOperationException("Mysql requires V2")
    }

    @Throws(Exception::class)
    override fun insertRecordsInternalV2(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    ) {
        if (records.isEmpty()) {
            return
        }

        verifyLocalFileEnabled(database)
        try {
            val tmpFile = Files.createTempFile("$tableName-", ".tmp").toFile()

            loadDataIntoTable(
                database,
                records,
                schemaName,
                tableName,
                tmpFile,
                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                JavaBaseConstants.COLUMN_NAME_DATA,
                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
                JavaBaseConstants.COLUMN_NAME_AB_META
            )
            Files.delete(tmpFile.toPath())
        } catch (e: IOException) {
            throw SQLException(e)
        }
    }

    @Throws(SQLException::class)
    private fun loadDataIntoTable(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tmpTableName: String?,
        tmpFile: File,
        vararg columnNames: String
    ) {
        database.execute { connection: Connection ->
            try {
                writeBatchToFile(tmpFile, records)

                val absoluteFile = "'" + tmpFile.absolutePath + "'"

                /*
                 * We want to generate a query like:
                 *
                 * LOAD DATA LOCAL INFILE '/a/b/c' INTO TABLE foo.bar FIELDS TERMINATED BY ',' ENCLOSED BY
                 * '"' ESCAPED BY '\"' LINES TERMINATED BY '\r\n' (@c0, @c1, @c2, @c3, @c4) SET _airybte_raw_id =
                 * NULLIF(@c0, ''), _airbyte_data = NULLIF(@c1, ''), _airbyte_extracted_at = NULLIF(@c2, ''),
                 * _airbyte_loaded_at = NULLIF(@c3, ''), _airbyte_meta = NULLIF(@c4, '')
                 *
                 * This is to avoid weird default values (e.g. 0000-00-00 00:00:00) when the value should be NULL.
                 */
                val colVarDecls =
                    ("(" +
                        IntStream.range(0, columnNames.size)
                            .mapToObj { i: Int -> "@c$i" }
                            .collect(Collectors.joining(",")) +
                        ")")
                val colAssignments =
                    IntStream.range(0, columnNames.size)
                        .mapToObj { i: Int -> columnNames[i] + " = NULLIF(@c" + i + ", '')" }
                        .collect(Collectors.joining(","))

                val query =
                    String.format(
                        """
            LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s
            FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY '\${'"'}'
            LINES TERMINATED BY '\r\
            '
            %s
            SET
            %s
            
            """.trimIndent(),
                        absoluteFile,
                        schemaName,
                        tmpTableName,
                        colVarDecls,
                        colAssignments
                    )
                connection.createStatement().use { stmt -> stmt.execute(query) }
            } catch (e: Exception) {
                throw RuntimeException(e)
            }
        }
    }

    @Throws(SQLException::class)
    fun verifyLocalFileEnabled(database: JdbcDatabase) {
        val localFileEnabled = isLocalFileEnabled || checkIfLocalFileIsEnabled(database)
        if (!localFileEnabled) {
            tryEnableLocalFile(database)
        }
        isLocalFileEnabled = true
    }

    @Throws(SQLException::class)
    private fun tryEnableLocalFile(database: JdbcDatabase) {
        database.execute { connection: Connection ->
            try {
                connection.createStatement().use { statement ->
                    statement.execute("set global local_infile=true")
                }
            } catch (e: Exception) {
                throw RuntimeException(
                    "The DB user provided to airbyte was unable to switch on the local_infile attribute on the MySQL server. As an admin user, you will need to run \"SET GLOBAL local_infile = true\" before syncing data with Airbyte.",
                    e
                )
            }
        }
    }

    @Throws(SQLException::class)
    private fun getVersion(database: JdbcDatabase): Double {
        val versions =
            database.queryStrings(
                { connection: Connection ->
                    connection.createStatement().executeQuery("select version()")
                },
                { resultSet: ResultSet -> resultSet.getString("version()") }
            )
        return versions[0].substring(0, 3).toDouble()
    }

    @Throws(SQLException::class)
    fun isCompatibleVersion(database: JdbcDatabase): VersionCompatibility {
        val version = getVersion(database)
        return VersionCompatibility(version, version >= 5.7)
    }

    override val isSchemaRequired: Boolean
        get() = false

    @Throws(SQLException::class)
    private fun checkIfLocalFileIsEnabled(database: JdbcDatabase): Boolean {
        val localFiles =
            database.queryStrings(
                { connection: Connection ->
                    connection
                        .createStatement()
                        .executeQuery("SHOW GLOBAL VARIABLES LIKE 'local_infile'")
                },
                { resultSet: ResultSet -> resultSet.getString("Value") }
            )
        return localFiles[0].equals("on", ignoreCase = true)
    }

    @Throws(SQLException::class)
    override fun createTableIfNotExists(
        database: JdbcDatabase,
        schemaName: String?,
        tableName: String?
    ) {
        super.createTableIfNotExists(database, schemaName, tableName)

        // mysql doesn't have a "create index if not exists" method, and throws an error
        // if you create an index that already exists.
        // So we can't just override postCreateTableQueries.
        // Instead, we manually query for index existence and create the index if needed.
        // jdbc metadata is... weirdly painful to use for finding indexes:
        // (getIndexInfo requires isUnique / isApproximate, which sounds like an easy thing to get
        // wrong),
        // and jooq doesn't support `show` queries,
        // so manually build the query string. We can at least use jooq to render the table name.
        val tableId = DSL.using(SQLDialect.MYSQL).render(DSL.table(DSL.name(schemaName, tableName)))
        // This query returns a list of columns in the index, or empty list if the index does not
        // exist.
        val unloadedExtractedAtIndexNotExists =
            database
                .queryJsons("show index from $tableId where key_name='unloaded_extracted_at'")
                .isEmpty()
        if (unloadedExtractedAtIndexNotExists) {
            database.execute(
                DSL.using(SQLDialect.MYSQL)
                    .createIndex("unloaded_extracted_at")
                    .on(
                        DSL.table(DSL.name(schemaName, tableName)),
                        DSL.field(DSL.name(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)),
                        DSL.field(DSL.name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT))
                    )
                    .sql
            )
        }
        val extractedAtIndexNotExists =
            database.queryJsons("show index from $tableId where key_name='extracted_at'").isEmpty()
        if (extractedAtIndexNotExists) {
            database.execute(
                DSL.using(SQLDialect.MYSQL)
                    .createIndex("extracted_at")
                    .on(
                        DSL.table(DSL.name(schemaName, tableName)),
                        DSL.field(DSL.name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT))
                    )
                    .getSQL()
            )
        }
    }

    override fun createTableQueryV1(schemaName: String?, tableName: String?): String {
        throw UnsupportedOperationException("Mysql requires V2")
    }

    override fun createTableQueryV2(schemaName: String?, tableName: String?): String {
        // MySQL requires byte information with VARCHAR. Since we are using uuid as value for the
        // column,
        // 256 is enough
        return String.format(
            """
        CREATE TABLE IF NOT EXISTS %s.%s ( 
        %s VARCHAR(256) PRIMARY KEY,
        %s JSON,
        %s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
        %s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
        %s JSON
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

    class VersionCompatibility(val version: Double, val isCompatible: Boolean)
}
