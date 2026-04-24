/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.write.load

import com.amazonaws.services.s3.model.ObjectMetadata
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.redshift2.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.OutputStreamWriter
import java.nio.charset.StandardCharsets
import java.time.Instant
import java.util.UUID
import java.util.zip.GZIPOutputStream
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

private val logger = KotlinLogging.logger {}

internal val CSV_FORMAT: CSVFormat = CSVFormat.DEFAULT
internal const val DEFAULT_FLUSH_LIMIT = 1_000_000

/**
 * Buffers records into a gzip-compressed CSV file and flushes them to Redshift via S3 staging.
 *
 * The loading pipeline works as follows:
 * 1. Records are accumulated into an in-memory gzip-compressed CSV buffer
 * 2. On [flush], the buffer is uploaded to S3 as a `.csv.gz` file
 * 3. A Redshift `COPY` command loads the data from S3 into the target table
 * 4. The staging S3 object is optionally deleted (based on [purgeStagingData])
 *
 * The CSV format includes a header row (column names), which Redshift skips via `IGNOREHEADER 1`
 * in the generated COPY command.
 */
class RedshiftInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val redshiftClient: RedshiftAirbyteClient,
    private val configuration: RedshiftConfiguration,
    private val flushLimit: Int = DEFAULT_FLUSH_LIMIT,
) {

    private val formatter = RedshiftSchemaRecordFormatter(columns)
    private val s3Config = configuration.uploadingMethod!!
    private val purgeStagingData: Boolean = s3Config.purgeStagingData ?: true

    /** In-memory byte buffer backing the gzip CSV output. */
    private var byteBuffer: ByteArrayOutputStream? = null
    private var gzipOutputStream: GZIPOutputStream? = null
    private var csvPrinter: CSVPrinter? = null

    internal var recordCount = 0

    /**
     * Adds a record to the current CSV batch.
     *
     * On the first call, initializes the gzip CSV buffer and writes a header row containing column
     * names. Subsequent calls format the record and append it as a CSV row. The CSV printer is
     * flushed every [flushLimit] records to manage memory.
     */
    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (byteBuffer == null) {
            initializeBuffer()
        }

        csvPrinter!!.printRecord(formatter.format(recordFields))
        recordCount++

        if (recordCount % flushLimit == 0) {
            csvPrinter!!.flush()
        }
    }

    /**
     * Flushes the buffered CSV data to Redshift via S3 staging.
     *
     * Steps:
     * 1. Finalize and close the gzip CSV buffer
     * 2. Upload the compressed bytes to S3
     * 3. Execute Redshift COPY to load the data from S3
     * 4. Optionally delete the S3 staging file
     * 5. Reset internal state for the next batch
     */
    suspend fun flush() {
        val buffer = byteBuffer
        if (buffer == null) {
            logger.warn { "No data to flush for ${tableName.namespace}.${tableName.name}" }
            return
        }

        try {
            // Step 1: Finalize the gzip CSV
            csvPrinter?.flush()
            csvPrinter?.close()
            gzipOutputStream?.finish()
            gzipOutputStream?.close()

            val csvBytes = buffer.toByteArray()
            val s3Key = buildStagingS3Key()
            val s3Path = "s3://${s3Config.s3BucketName}/$s3Key"

            logger.info {
                "Uploading $recordCount record(s) (${csvBytes.size} bytes compressed) " +
                    "for ${tableName.namespace}.${tableName.name} to $s3Path"
            }

            // Step 2: Upload to S3
            val metadata =
                ObjectMetadata().apply {
                    contentLength = csvBytes.size.toLong()
                    contentType = "application/gzip"
                }
            redshiftClient.uploadToS3(s3Config.s3BucketName, s3Key, csvBytes, metadata)

            // Step 3: Execute COPY
            redshiftClient.copyFromS3(
                tableName = tableName,
                s3Path = s3Path,
                accessKeyId = s3Config.accessKeyId,
                secretAccessKey = s3Config.secretAccessKey,
                region = s3Config.s3BucketRegion!!,
            )

            logger.info {
                "Loaded $recordCount row(s) into ${tableName.namespace}.${tableName.name}"
            }

            // Step 4: Cleanup S3 staging file
            if (purgeStagingData) {
                redshiftClient.deleteFromS3(s3Config.s3BucketName, s3Key)
                logger.debug { "Purged staging file: $s3Key" }
            }
        } catch (e: Exception) {
            logger.error(e) {
                "Failed to flush $recordCount record(s) for " +
                    "${tableName.namespace}.${tableName.name}"
            }
            throw e
        } finally {
            // Step 5: Reset state
            resetState()
        }
    }

    /**
     * Initializes the in-memory gzip CSV buffer and writes the header row.
     *
     * The header row contains all column names in the table's ordinal order. Redshift's COPY
     * command skips it via `IGNOREHEADER 1`.
     */
    private fun initializeBuffer() {
        byteBuffer = ByteArrayOutputStream()
        gzipOutputStream = GZIPOutputStream(byteBuffer)
        csvPrinter =
            CSVPrinter(OutputStreamWriter(gzipOutputStream!!, StandardCharsets.UTF_8), CSV_FORMAT)
        csvPrinter!!.printRecord(columns)
    }

    /**
     * Builds the S3 key for the staging file, respecting the configured bucket path prefix.
     *
     * Format: `{bucketPath}/{namespace}/{tableName}/{timestamp}_{uuid}.csv.gz`
     */
    private fun buildStagingS3Key(): String {
        val prefix =
            s3Config.s3BucketPath?.let { path ->
                val trimmed = path.trimEnd('/')
                if (trimmed.isNotEmpty()) "$trimmed/" else ""
            }
                ?: ""
        val timestamp = Instant.now().toEpochMilli()
        val uniqueId = UUID.randomUUID().toString().replace("-", "").take(8)
        return "${prefix}${tableName.namespace}/${tableName.name}/${timestamp}_$uniqueId.csv.gz"
    }

    /** Resets all internal state for the next batch. */
    private fun resetState() {
        csvPrinter = null
        gzipOutputStream = null
        byteBuffer = null
        recordCount = 0
    }
}
