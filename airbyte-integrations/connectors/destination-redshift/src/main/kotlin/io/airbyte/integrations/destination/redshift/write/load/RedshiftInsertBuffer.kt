/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.load

import de.siegmar.fastcsv.writer.CsvWriter
import de.siegmar.fastcsv.writer.LineDelimiter
import de.siegmar.fastcsv.writer.QuoteStrategies
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.redshift.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.text.SimpleDateFormat
import java.time.Instant
import java.util.*
import java.util.zip.GZIPOutputStream

private val logger = KotlinLogging.logger {}

private const val STAGING_FILE_EXTENSION = ".csv.gz"
private const val DATE_FORMAT = "yyyy_MM_dd"
private const val UTC = "UTC"
private const val CSV_WRITER_BUFFER_SIZE = 1024 * 1024 // 1 MB

/** Regex matching extended placeholders like `{date:yyyy_MM}` or `{timestamp:millis}`. */
private val EXTENDED_PLACEHOLDER_PATTERN = Regex("""\{(date:.+?|timestamp:.+?)\}""")

/**
 * Buffers records into a gzip-compressed CSV file and flushes them to Redshift via S3 staging.
 *
 * The loading pipeline works as follows:
 * 1. Records are accumulated into an in-memory gzip-compressed CSV buffer
 * 2. On [flush], the buffer is uploaded to S3 as a `.csv.gz` file
 * 3. A Redshift `COPY` command loads the data from S3 into the target table
 * 4. The staging S3 object is optionally deleted (based on [purgeStagingData])
 */
class RedshiftInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val redshiftClient: RedshiftAirbyteClient,
    private val configuration: RedshiftConfiguration,
) {

    private val formatter = RedshiftSchemaRecordFormatter(columns)
    private val s3Config = configuration.uploadingMethod!!
    private val purgeStagingData: Boolean = s3Config.purgeStagingData ?: true

    /** In-memory byte buffer backing the gzip CSV output. */
    private var byteBuffer: ByteArrayOutputStream? = null
    private var gzipOutputStream: GZIPOutputStream? = null
    private var csvWriter: CsvWriter? = null

    private val csvWriterBuilder =
        CsvWriter.builder()
            .bufferSize(CSV_WRITER_BUFFER_SIZE)
            .fieldSeparator(',')
            .quoteCharacter('"')
            .lineDelimiter(LineDelimiter.LF)
            .quoteStrategy(QuoteStrategies.REQUIRED)

    internal var recordCount = 0
    private var partNumber = 0

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

        csvWriter!!.writeRecord(formatter.format(recordFields).map { it.toString() })
        recordCount++
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
            csvWriter?.flush()
            csvWriter?.close()
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
            redshiftClient.uploadToS3(s3Config.s3BucketName, s3Key, csvBytes)

            // Step 3: Execute COPY
            redshiftClient.copyFromS3(
                tableName = tableName,
                s3Path = s3Path,
                accessKeyId = s3Config.accessKeyId,
                secretAccessKey = s3Config.secretAccessKey,
                region = s3Config.s3BucketRegion,
            )

            logger.info { "Loaded data into ${tableName.namespace}.${tableName.name}" }

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
     *
     * Uses [CompressionOutputStream] (64 KB buffer, compression level 5) to reduce CPU spent in
     * native zlib deflate.
     */
    private fun initializeBuffer() {
        val buffer = ByteArrayOutputStream()
        val gzip = CompressionOutputStream(buffer)
        val writer = csvWriterBuilder.build(gzip)
        writer.writeRecord(columns)
        byteBuffer = buffer
        gzipOutputStream = gzip
        csvWriter = writer
    }

    /**
     * Builds the S3 key for the staging file, respecting the configured bucket path prefix.
     *
     * The key is composed of two parts:
     * - **Directory**: `{bucketPath}/{namespace}/{tableName}/` (always hardcoded)
     * - **Filename**: resolved from [S3StagingConfiguration.fileNamePattern] if set, otherwise
     * falls back to a default `{timestamp}_{uuid}.csv.gz` format.
     *
     * Supported filename pattern tokens (matching v1 parity):
     * - `{date}` — UTC date formatted as `yyyy_MM_dd`
     * - `{date:<format>}` — UTC date with a custom [SimpleDateFormat] pattern
     * - `{timestamp}` — epoch milliseconds
     * - `{timestamp:millis}` — epoch milliseconds (explicit)
     * - `{timestamp:micro}` — epoch microseconds
     * - `{sync_id}` — value of `WORKER_JOB_ID` environment variable
     * - `{format_extension}` — `.csv.gz`
     * - `{part_number}` — monotonically increasing part counter per buffer instance
     *
     * If the resolved filename does not end with `.csv.gz`, the extension is appended automatically
     * so that Redshift's COPY command can detect the compression format.
     */
    internal fun buildStagingS3Key(): String {
        val prefix =
            s3Config.s3BucketPath?.let { path ->
                val trimmed = path.trimEnd('/')
                if (trimmed.isNotEmpty()) "$trimmed/" else ""
            }
                ?: ""
        val directory = "${prefix}${tableName.namespace}/${tableName.name}/"
        val fileName = resolveFileName()
        partNumber++
        return "$directory$fileName"
    }

    /**
     * Resolves the staging filename.
     *
     * If [S3StagingConfiguration.fileNamePattern] is null or blank, returns a default filename
     * using timestamp and a short UUID for uniqueness. Otherwise, resolves the pattern by
     * substituting supported `{token}` placeholders — matching the behavior of the legacy
     * [S3FilenameTemplateManager] used by Redshift v1.
     */
    private fun resolveFileName(): String {
        val pattern = s3Config.fileNamePattern
        if (pattern.isNullOrBlank()) {
            val timestamp = Instant.now().toEpochMilli()
            val uniqueId = UUID.randomUUID().toString().replace("-", "").take(8)
            return "${timestamp}_$uniqueId$STAGING_FILE_EXTENSION"
        }

        val millis = Instant.now().toEpochMilli()
        var resolved = pattern.trim().replace(" ", "_")

        // Step 1: Resolve extended placeholders ({date:<format>}, {timestamp:millis|micro})
        resolved =
            EXTENDED_PLACEHOLDER_PATTERN.replace(resolved) { match ->
                val parts = match.groupValues[1].split(":", limit = 2)
                when (parts[0].lowercase()) {
                    "date" -> {
                        val fmt =
                            SimpleDateFormat(parts[1]).apply {
                                timeZone = TimeZone.getTimeZone(UTC)
                            }
                        fmt.format(millis)
                    }
                    "timestamp" ->
                        when (parts[1]) {
                            "millis" -> millis.toString()
                            "micro" -> (millis * 1000).toString()
                            else -> match.value
                        }
                    else -> match.value
                }
            }

        // Step 2: Resolve standard placeholders
        val defaultDateFmt =
            SimpleDateFormat(DATE_FORMAT).apply { timeZone = TimeZone.getTimeZone(UTC) }
        resolved =
            resolved
                .replace("{date}", defaultDateFmt.format(millis))
                .replace("{timestamp}", millis.toString())
                .replace("{sync_id}", System.getenv("WORKER_JOB_ID") ?: "")
                .replace("{format_extension}", STAGING_FILE_EXTENSION)
                .replace("{part_number}", partNumber.toString())

        // Step 3: Ensure the file has the correct extension for Redshift COPY
        if (!resolved.endsWith(STAGING_FILE_EXTENSION)) {
            resolved += STAGING_FILE_EXTENSION
        }

        return resolved
    }

    /** Resets all internal state for the next batch. */
    private fun resetState() {
        csvWriter = null
        gzipOutputStream = null
        byteBuffer = null
        recordCount = 0
    }
}

/**
 * [GZIPOutputStream] with a 64 KB buffer (vs. 512 bytes default) and compression level 5 to reduce
 * zlib JNI overhead for ephemeral staging files.
 */
private class CompressionOutputStream(
    out: OutputStream,
    bufferSize: Int = 65_536,
) : GZIPOutputStream(out, bufferSize) {
    init {
        def.setLevel(5)
    }
}
