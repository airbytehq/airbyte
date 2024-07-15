/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.operation

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.commons.string.Strings.join
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabaseUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.sql.SQLException
import java.util.*

private val log = KotlinLogging.logger {}

/** Client wrapper providing Snowflake Stage related operations. */
class SnowflakeStagingClient(private val database: JdbcDatabase) {

    private data class CopyIntoTableResult(
        val file: String,
        val copyStatus: CopyStatus,
        val rowsParsed: Int,
        val rowsLoaded: Int,
        val errorsSeen: Int,
        val firstError: String?
    )

    private enum class CopyStatus {
        UNKNOWN,
        LOADED,
        LOAD_FAILED,
        PARTIALLY_LOADED
    }

    // Most of the code here is preserved from
    // https://github.com/airbytehq/airbyte/blob/503b819b846663b0dff4c90322d0219a93e61d14/airbyte-integrations/connectors/destination-snowflake/src/main/java/io/airbyte/integrations/destination/snowflake/SnowflakeInternalStagingSqlOperations.java
    @Throws(IOException::class)
    fun uploadRecordsToStage(
        recordsData: SerializableBuffer,
        stageName: String,
        stagingPath: String
    ): String {
        val exceptionsThrown: MutableList<Exception> = ArrayList()
        var succeeded = false
        while (exceptionsThrown.size < UPLOAD_RETRY_LIMIT && !succeeded) {
            try {
                uploadRecordsToBucket(stageName, stagingPath, recordsData)
                succeeded = true
            } catch (e: Exception) {
                log.error(e) { "Failed to upload records into stage $stagingPath" }
                exceptionsThrown.add(e)
            }
            if (!succeeded) {
                log.info {
                    "Retrying to upload records into stage $stagingPath (${exceptionsThrown.size}/$UPLOAD_RETRY_LIMIT})"
                }
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
        log.info {
            "Successfully loaded records to stage $stagingPath with ${exceptionsThrown.size} re-attempt(s)"
        }
        return recordsData.filename
    }

    @Throws(Exception::class)
    private fun uploadRecordsToBucket(
        stageName: String,
        stagingPath: String,
        recordsData: SerializableBuffer
    ) {
        val query = getPutQuery(stageName, stagingPath, recordsData.file!!.absolutePath)
        val queryId = UUID.randomUUID()
        log.info { "executing query $queryId, $query" }
        val results = database.queryJsons(query)
        if (results.isNotEmpty() && (results.first().has("source_size"))) {
            if (results.first().get("source_size").asLong() == 0L) {
                // TODO: Should we break the Sync rather than proceeding with empty file for COPY ?
                log.warn {
                    "query $queryId, uploaded an empty file, no new records will be inserted"
                }
            }
        }
        log.info { "query $queryId, completed with $results" }
        if (!checkStageObjectExists(stageName, stagingPath, recordsData.filename)) {
            log.error {
                "Failed to upload data into stage, object @${
                    (stagingPath + "/" + recordsData.filename).replace(
                        "/+".toRegex(),
                        "/",
                    )
                } not found"
            }
            throw RuntimeException("Upload failed")
        }
    }

    internal fun getPutQuery(stageName: String, stagingPath: String, filePath: String): String {
        return String.format(
            PUT_FILE_QUERY,
            filePath,
            stageName,
            stagingPath,
            // max allowed param is 99, we don't need so many threads for a single file upload
            minOf(Runtime.getRuntime().availableProcessors(), 4)
        )
    }

    @Throws(SQLException::class)
    private fun checkStageObjectExists(
        stageName: String,
        stagingPath: String,
        filename: String
    ): Boolean {
        val query = getListQuery(stageName, stagingPath, filename)
        log.debug { "Executing query: $query" }
        val result: Boolean
        database.unsafeQuery(query).use { stream -> result = stream.findAny().isPresent }
        return result
    }

    /**
     * Creates a SQL query to list file which is staged
     *
     * @param stageName name of staging folder
     * @param stagingPath path to the files within the staging folder
     * @param filename name of the file within staging area
     * @return SQL query string
     */
    internal fun getListQuery(stageName: String, stagingPath: String, filename: String): String {
        return String.format(LIST_STAGE_QUERY, stageName, stagingPath, filename)
            .replace("/+".toRegex(), "/")
    }

    @Throws(Exception::class)
    fun createStageIfNotExists(stageName: String) {
        val query = getCreateStageQuery(stageName)
        log.debug { "Executing query: $query" }
        try {
            database.execute(query)
        } catch (e: Exception) {
            throw SnowflakeDatabaseUtils.checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    /**
     * Creates a SQL query to create a staging folder. This query will create a staging folder if
     * one previously did not exist
     *
     * @param stageName name of the staging folder
     * @return SQL query string
     */
    internal fun getCreateStageQuery(stageName: String): String {
        return String.format(CREATE_STAGE_QUERY, stageName)
    }

    @Throws(SQLException::class)
    fun copyIntoTableFromStage(
        stageName: String,
        stagingPath: String,
        stagedFiles: List<String>,
        streamId: StreamId
    ) {
        try {
            val queryId = UUID.randomUUID()
            val query = getCopyQuery(stageName, stagingPath, stagedFiles, streamId)
            log.info { "query $queryId, $query" }
            // queryJsons is intentionally used here to get the error message in case of failure
            // instead of execute
            val results = database.queryJsons(query)
            if (results.isNotEmpty()) {
                // There will be only one row returned as the result of COPY INTO query
                val copyResult = getCopyResult(results.first())
                when (copyResult.copyStatus) {
                    CopyStatus.LOADED ->
                        log.info {
                            "query $queryId, successfully loaded ${copyResult.rowsLoaded} rows of data into table"
                        }
                    CopyStatus.LOAD_FAILED -> {
                        log.error {
                            "query $queryId, failed to load data into table, " +
                                "rows_parsed: ${copyResult.rowsParsed}, " +
                                "rows_loaded: ${copyResult.rowsLoaded} " +
                                "errors: ${copyResult.errorsSeen}, " +
                                "firstError: ${copyResult.firstError}"
                        }
                        throw Exception(
                            "COPY into table failed with ${copyResult.errorsSeen} errors, check logs"
                        )
                    }
                    else -> log.warn { "query $queryId, unrecognized result format, $results" }
                }
            } else {
                log.warn { "query $queryId, no result returned" }
            }
        } catch (e: SQLException) {
            throw SnowflakeDatabaseUtils.checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    private fun getCopyResult(result: JsonNode): CopyIntoTableResult {
        if (
            result.has("file") &&
                result.has("status") &&
                result.has("rows_parsed") &&
                result.has("rows_loaded") &&
                result.has("errors_seen")
        ) {
            val status =
                when (result.get("status").asText()) {
                    "LOADED" -> CopyStatus.LOADED
                    "LOAD_FAILED" -> CopyStatus.LOAD_FAILED
                    "PARTIALLY_LOADED" -> CopyStatus.PARTIALLY_LOADED
                    else -> CopyStatus.UNKNOWN
                }
            return CopyIntoTableResult(
                result.get("file").asText(),
                status,
                result.get("rows_parsed").asInt(),
                result.get("rows_loaded").asInt(),
                result.get("errors_seen").asInt(),
                if (result.has("first_error")) result.get("first_error").asText() else null
            )
        } else {
            // Safety in case snowflake decides to change the response format
            // instead of blowing up, we return a default object
            return CopyIntoTableResult("", CopyStatus.UNKNOWN, 0, 0, 0, null)
        }
    }

    /**
     * Creates a SQL query to bulk copy data into fully qualified destination table See
     * https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html for more context
     *
     * @param stageName name of staging folder
     * @param stagingPath path of staging folder to data files
     * @param stagedFiles collection of the staging files
     * @param streamId
     * @return SQL query string
     */
    internal fun getCopyQuery(
        stageName: String,
        stagingPath: String,
        stagedFiles: List<String>,
        streamId: StreamId
    ): String {
        return String.format(
            COPY_QUERY_1S1T + generateFilesList(stagedFiles) + ";",
            streamId.rawNamespace,
            streamId.rawName,
            stageName,
            stagingPath
        )
    }

    // TODO: Do we need this sketchy logic when all we use is just 1 file.
    private fun generateFilesList(files: List<String>): String {
        if (0 < files.size && files.size < MAX_FILES_IN_LOADING_QUERY_LIMIT) {
            // see
            // https://docs.snowflake.com/en/user-guide/data-load-considerations-load.html#lists-of-files
            val filesString =
                files.joinToString { filename: String ->
                    "'${
                    filename.substring(
                        filename.lastIndexOf("/") + 1,
                    )
                }'"
                }
            return " files = ($filesString)"
        } else {
            return ""
        }
    }

    @Throws(Exception::class)
    fun dropStageIfExists(stageName: String) {
        try {
            val query = getDropQuery(stageName)
            log.debug { "Executing query: $query" }
            database.execute(query)
        } catch (e: SQLException) {
            throw SnowflakeDatabaseUtils.checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    /**
     * Creates a SQL query to drop staging area and all associated files within the staged area
     * https://docs.snowflake.com/en/sql-reference/sql/drop-stage
     * @param stageName name of staging folder
     * @return SQL query string
     */
    internal fun getDropQuery(stageName: String?): String {
        return String.format(DROP_STAGE_QUERY, stageName)
    }

    companion object {
        private const val UPLOAD_RETRY_LIMIT: Int = 3
        private const val MAX_FILES_IN_LOADING_QUERY_LIMIT = 1000
        private const val CREATE_STAGE_QUERY =
            "CREATE STAGE IF NOT EXISTS %s encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');"
        private const val PUT_FILE_QUERY = "PUT file://%s @%s/%s PARALLEL = %d;"
        private const val LIST_STAGE_QUERY = "LIST @%s/%s/%s;"

        // the 1s1t copy query explicitly quotes the raw table+schema name.
        // TODO: https://github.com/airbytehq/airbyte/issues/36410 for improved error handling.
        private val COPY_QUERY_1S1T =
            """
            |COPY INTO "%s"."%s" FROM '@%s/%s'
            |file_format = (
            |   type = csv
            |   compression = auto
            |   field_delimiter = ','
            |   skip_header = 0
            |   FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            |   NULL_IF=('')
            |)
            """.trimMargin()
        private const val DROP_STAGE_QUERY = "DROP STAGE IF EXISTS %s;"
    }
}
