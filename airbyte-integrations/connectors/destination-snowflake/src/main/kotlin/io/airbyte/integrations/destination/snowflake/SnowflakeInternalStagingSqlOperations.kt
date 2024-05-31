/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.commons.string.Strings.join
import java.io.IOException
import java.sql.SQLException
import java.time.Instant
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
class SnowflakeInternalStagingSqlOperations(
    private val nameTransformer: NamingConventionTransformer
) : SnowflakeSqlStagingOperations() {
    override fun getStageName(namespace: String?, streamName: String?): String {
        return java.lang.String.join(
            ".",
            '"'.toString() + nameTransformer.convertStreamName(namespace!!) + '"',
            '"'.toString() + nameTransformer.convertStreamName(streamName!!) + '"'
        )
    }

    override fun getStagingPath(
        connectionId: UUID?,
        namespace: String?,
        streamName: String?,
        outputTableName: String?,
        writeDatetime: Instant?
    ): String? {
        // see https://docs.snowflake.com/en/user-guide/data-load-considerations-stage.html
        val zonedDateTime = ZonedDateTime.ofInstant(writeDatetime, ZoneOffset.UTC)
        return nameTransformer.applyDefaultCase(
            String.format(
                "%s/%02d/%02d/%02d/%s/",
                zonedDateTime.year,
                zonedDateTime.monthValue,
                zonedDateTime.dayOfMonth,
                zonedDateTime.hour,
                connectionId
            )
        )
    }

    @Throws(IOException::class)
    override fun uploadRecordsToStage(
        database: JdbcDatabase?,
        recordsData: SerializableBuffer?,
        schemaName: String?,
        stageName: String?,
        stagingPath: String?
    ): String {
        val exceptionsThrown: MutableList<Exception> = ArrayList()
        var succeeded = false
        while (exceptionsThrown.size < UPLOAD_RETRY_LIMIT && !succeeded) {
            try {
                uploadRecordsToBucket(database, stageName, stagingPath, recordsData)
                succeeded = true
            } catch (e: Exception) {
                LOGGER.error("Failed to upload records into stage {}", stagingPath, e)
                exceptionsThrown.add(e)
            }
            if (!succeeded) {
                LOGGER.info(
                    "Retrying to upload records into stage {} ({}/{}})",
                    stagingPath,
                    exceptionsThrown.size,
                    UPLOAD_RETRY_LIMIT
                )
            }
        }
        if (!succeeded) {
            throw RuntimeException(
                String.format(
                    "Exceptions thrown while uploading records into stage: %s",
                    join(exceptionsThrown, "\n")
                )
            )
        }
        LOGGER.info(
            "Successfully loaded records to stage {} with {} re-attempt(s)",
            stagingPath,
            exceptionsThrown.size
        )
        return recordsData!!.filename
    }

    @Throws(Exception::class)
    private fun uploadRecordsToBucket(
        database: JdbcDatabase?,
        stageName: String?,
        stagingPath: String?,
        recordsData: SerializableBuffer?
    ) {
        val query = getPutQuery(stageName, stagingPath, recordsData!!.file!!.absolutePath)
        LOGGER.debug("Executing query: {}", query)
        database!!.execute(query)
        if (!checkStageObjectExists(database, stageName, stagingPath, recordsData.filename)) {
            LOGGER.error(
                String.format(
                    "Failed to upload data into stage, object @%s not found",
                    (stagingPath + "/" + recordsData.filename).replace("/+".toRegex(), "/")
                )
            )
            throw RuntimeException("Upload failed")
        }
    }

    fun getPutQuery(stageName: String?, stagingPath: String?, filePath: String?): String {
        return String.format(
            PUT_FILE_QUERY,
            filePath,
            stageName,
            stagingPath,
            Runtime.getRuntime().availableProcessors()
        )
    }

    @Throws(SQLException::class)
    private fun checkStageObjectExists(
        database: JdbcDatabase?,
        stageName: String?,
        stagingPath: String?,
        filename: String
    ): Boolean {
        val query = getListQuery(stageName, stagingPath, filename)
        LOGGER.debug("Executing query: {}", query)
        val result: Boolean
        database!!.unsafeQuery(query).use { stream -> result = stream.findAny().isPresent }
        return result
    }

    /**
     * Creates a SQL query to list all files that have been staged
     *
     * @param stageName name of staging folder
     * @param stagingPath path to the files within the staging folder
     * @param filename name of the file within staging area
     * @return SQL query string
     */
    fun getListQuery(stageName: String?, stagingPath: String?, filename: String?): String {
        return String.format(LIST_STAGE_QUERY, stageName, stagingPath, filename)
            .replace("/+".toRegex(), "/")
    }

    @Throws(Exception::class)
    override fun createStageIfNotExists(database: JdbcDatabase?, stageName: String?) {
        val query = getCreateStageQuery(stageName)
        LOGGER.debug("Executing query: {}", query)
        try {
            database!!.execute(query)
        } catch (e: Exception) {
            throw checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    /**
     * Creates a SQL query to create a staging folder. This query will create a staging folder if
     * one previously did not exist
     *
     * @param stageName name of the staging folder
     * @return SQL query string
     */
    fun getCreateStageQuery(stageName: String?): String {
        return String.format(CREATE_STAGE_QUERY, stageName)
    }

    @Throws(SQLException::class)
    override fun copyIntoTableFromStage(
        database: JdbcDatabase?,
        stageName: String?,
        stagingPath: String?,
        stagedFiles: List<String>?,
        tableName: String?,
        schemaName: String?
    ) {
        try {
            val query = getCopyQuery(stageName, stagingPath, stagedFiles, tableName, schemaName)
            LOGGER.debug("Executing query: {}", query)
            database!!.execute(query)
        } catch (e: SQLException) {
            throw checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    /**
     * Creates a SQL query to bulk copy data into fully qualified destination table See
     * https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html for more context
     *
     * @param stageName name of staging folder
     * @param stagingPath path of staging folder to data files
     * @param stagedFiles collection of the staging files
     * @param dstTableName name of destination table
     * @param schemaName name of schema
     * @return SQL query string
     */
    fun getCopyQuery(
        stageName: String?,
        stagingPath: String?,
        stagedFiles: List<String>?,
        dstTableName: String?,
        schemaName: String?
    ): String {
        return String.format(
            COPY_QUERY_1S1T + generateFilesList(stagedFiles!!) + ";",
            schemaName,
            dstTableName,
            stageName,
            stagingPath
        )
    }

    @Throws(Exception::class)
    override fun dropStageIfExists(
        database: JdbcDatabase?,
        stageName: String?,
        stagingPath: String?
    ) {
        try {
            val query = getDropQuery(stageName)
            LOGGER.debug("Executing query: {}", query)
            database!!.execute(query)
        } catch (e: SQLException) {
            throw checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    /**
     * Creates a SQL query to drop staging area and all associated files within the staged area
     *
     * @param stageName name of staging folder
     * @return SQL query string
     */
    fun getDropQuery(stageName: String?): String {
        return String.format(DROP_STAGE_QUERY, stageName)
    }

    /**
     * Creates a SQL query used to remove staging files that were just staged See
     * https://docs.snowflake.com/en/sql-reference/sql/remove.html for more context
     *
     * @param stageName name of staging folder
     * @return SQL query string
     */
    fun getRemoveQuery(stageName: String?): String {
        return String.format(REMOVE_QUERY, stageName)
    }

    companion object {
        const val UPLOAD_RETRY_LIMIT: Int = 3

        private const val CREATE_STAGE_QUERY =
            "CREATE STAGE IF NOT EXISTS %s encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');"
        private const val PUT_FILE_QUERY = "PUT file://%s @%s/%s PARALLEL = %d;"
        private const val LIST_STAGE_QUERY = "LIST @%s/%s/%s;"

        // the 1s1t copy query explicitly quotes the raw table+schema name.
        // we set error_on_column_count_mismatch because (at time of writing), we haven't yet added
        // the airbyte_meta column to the raw table.
        // See also https://github.com/airbytehq/airbyte/issues/36410 for improved error handling.
        // TODO remove error_on_column_count_mismatch once snowflake has airbyte_meta in raw data.
        private val COPY_QUERY_1S1T =
            """
      COPY INTO "%s"."%s" FROM '@%s/%s'
      file_format = (
        type = csv
        compression = auto
        field_delimiter = ','
        skip_header = 0
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        NULL_IF=('')
        error_on_column_count_mismatch=false
      )
      """.trimIndent()
        private const val DROP_STAGE_QUERY = "DROP STAGE IF EXISTS %s;"
        private const val REMOVE_QUERY = "REMOVE @%s;"

        private val LOGGER: Logger = LoggerFactory.getLogger(SnowflakeSqlOperations::class.java)
    }
}
