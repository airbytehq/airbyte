/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write.load

import de.siegmar.fastcsv.writer.CsvWriter
import de.siegmar.fastcsv.writer.LineDelimiter
import de.siegmar.fastcsv.writer.QuoteStrategies
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.databricksv2.client.DatabricksAirbyteClient
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.time.Instant
import java.time.ZoneOffset
import java.util.*
import java.util.zip.GZIPOutputStream

private val logger = KotlinLogging.logger {}

private const val CSV_WRITER_BUFFER_SIZE = 1024 * 1024 // 1 MB
private const val STAGING_FILE_EXTENSION = ".csv.gz"
private const val VOLUMES_BASE_PATH = "/Volumes"

/**
 * Buffers records into an in-memory gzip-compressed CSV and flushes them to Databricks via Unity
 * Catalog Volume staging.
 *
 * The loading pipeline works as follows:
 * 1. Records are accumulated into an in-memory gzip-compressed CSV buffer
 * 2. On [flush], the buffer is uploaded to a Unity Catalog Volume as a `.csv.gz` file
 * 3. A Databricks `COPY INTO` command loads the data from the Volume into the target table
 * 4. The staging file is optionally deleted (based on [DatabricksV2Configuration.purgeStagingData])
 */
class DatabricksInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val databricksClient: DatabricksAirbyteClient,
    private val config: DatabricksV2Configuration,
) {

    /** In-memory byte buffer backing the gzip CSV output. */
    private var byteBuffer: ByteArrayOutputStream? = null
    private var gzipOutputStream: GZIPOutputStream? = null
    private var csvWriter: CsvWriter? = null
    internal var recordCount = 0

    private val csvWriterBuilder =
        CsvWriter.builder()
            .bufferSize(CSV_WRITER_BUFFER_SIZE)
            .fieldSeparator(',')
            .quoteCharacter('"')
            .lineDelimiter(LineDelimiter.LF)
            .quoteStrategy(QuoteStrategies.REQUIRED)

    /**
     * Adds a record to the current CSV batch.
     *
     * On the first call, initializes the gzip CSV buffer and writes a header row containing column
     * names. Subsequent calls format the record and append it as a CSV row.
     */
    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (byteBuffer == null) {
            initializeBuffer()
        }

        csvWriter!!.writeRecord(columns.map { col -> recordFields[col].toCsvValue().toString() })
        recordCount++
    }

    /** Flushes the buffered CSV data to Databricks via Unity Catalog Volume staging */
    suspend fun flush() {
        val buffer = byteBuffer
        if (buffer == null) {
            logger.warn { "No data to flush for ${tableName.namespace}.${tableName.name}" }
            return
        }

        try {
            // Finalize the gzip CSV
            csvWriter?.flush()
            csvWriter?.close()
            gzipOutputStream?.finish()
            gzipOutputStream?.close()

            val csvBytes = buffer.toByteArray()
            val stagingDir = stagingDirectory(tableName, config.database)
            val fileName = "${UUID.randomUUID()}$STAGING_FILE_EXTENSION"
            val stagedFilePath = "$stagingDir/$fileName"

            logger.info {
                "Uploading $recordCount record(s) (${csvBytes.size} bytes compressed) " +
                    "for ${tableName.namespace}.${tableName.name} to $stagedFilePath"
            }

            // Ensure staging volume and directory exist
            databricksClient.createStagingVolume(tableName, stagingDir)

            // Upload to Unity Catalog Volume
            databricksClient.uploadToVolume(
                stagedFilePath,
                ByteArrayInputStream(csvBytes),
            )

            // Execute COPY INTO
            databricksClient.copyFromVolume(tableName, stagedFilePath)

            logger.info {
                "Loaded $recordCount row(s) into ${tableName.namespace}.${tableName.name}"
            }

            // Cleanup staging file
            if (config.purgeStagingData) {
                databricksClient.deleteStagedFile(stagedFilePath)
                logger.debug { "Purged staging file: $stagedFilePath" }
            }
        } catch (e: Exception) {
            logger.error(e) {
                "Failed to flush $recordCount record(s) for " +
                    "${tableName.namespace}.${tableName.name}"
            }
            throw e
        } finally {
            resetState()
        }
    }

    /**
     * Initializes the in-memory gzip CSV buffer and writes the header row.
     *
     * Uses [CompressionOutputStream] (64 KB buffer, compression level 5) to reduce CPU spent in
     * native zlib deflate.
     */
    private fun initializeBuffer() {
        byteBuffer = ByteArrayOutputStream()
        gzipOutputStream = CompressionOutputStream(byteBuffer!!)
        csvWriter = csvWriterBuilder.build(gzipOutputStream!!).also { it.writeRecord(columns) }
    }

    /** Resets all internal state for the next batch. */
    private fun resetState() {
        csvWriter = null
        gzipOutputStream = null
        byteBuffer = null
        recordCount = 0
    }

    companion object {
        private val executionInstant = Instant.now()

        /**
         * Constructs the staging directory path within a Unity Catalog Volume. Format:
         * `/Volumes/<database>/<namespace>/<table>_staging/<year>_<month>_<day>`
         */
        fun stagingDirectory(tableName: TableName, database: String): String {
            val d = executionInstant.atZone(ZoneOffset.UTC).toLocalDate()
            return "$VOLUMES_BASE_PATH/$database/${tableName.namespace}/" +
                "${tableName.name}_staging/${d.year}_${d.monthValue}_${d.dayOfMonth}"
        }
    }
}

/** [GZIPOutputStream] with a 64 KB buffer and compression level 5. */
private class CompressionOutputStream(
    out: OutputStream,
) : GZIPOutputStream(out, 65_536) {
    init {
        def.setLevel(5)
    }
}
