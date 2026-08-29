/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.write.load

import de.siegmar.fastcsv.writer.CsvWriter
import de.siegmar.fastcsv.writer.LineDelimiter
import de.siegmar.fastcsv.writer.QuoteStrategies
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.firebolt.client.FireboltAirbyteClient
import io.airbyte.integrations.destination.firebolt.config.FireboltConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.text.SimpleDateFormat
import java.time.Instant
import java.util.*
import java.util.zip.GZIPOutputStream

private val log = KotlinLogging.logger {}

private const val STAGING_FILE_EXTENSION = ".csv.gz"
private const val DATE_FORMAT = "yyyy_MM_dd"
private const val UTC = "UTC"
private const val CSV_WRITER_BUFFER_SIZE = 1024 * 1024 // 1 MB

private val EXTENDED_PLACEHOLDER_PATTERN = Regex("""\{(date:.+?|timestamp:.+?)\}""")

/** Buffers records into a gzip-compressed CSV file and flushes them to Firebolt via S3 staging. */
class FireboltInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val fireboltClient: FireboltAirbyteClient,
    private val configuration: FireboltConfiguration,
) {

    private val formatter = FireboltRecordFormatter(columns)
    private val s3Config = configuration.s3Staging!!
    private val purgeStagingData: Boolean = s3Config.purgeStagingData ?: true

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

    /** Adds a record to the current CSV batch. */
    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (byteBuffer == null) {
            initializeBuffer()
        }

        csvWriter!!.writeRecord(formatter.format(recordFields).map { it.toString() })
        recordCount++
    }

    /** Flushes the buffered CSV data to Firebolt via S3 staging and COPY FROM. */
    suspend fun flush() {
        val buffer = byteBuffer
        if (buffer == null) {
            log.warn { "No data to flush for ${tableName.namespace}.${tableName.name}" }
            return
        }

        try {
            csvWriter?.flush()
            csvWriter?.close()
            gzipOutputStream?.finish()
            gzipOutputStream?.close()

            val csvBytes = buffer.toByteArray()
            val s3Key = buildStagingS3Key()
            val s3Path = "s3://${s3Config.s3BucketName}/$s3Key"

            log.info {
                "Uploading $recordCount record(s) (${csvBytes.size} bytes compressed) " +
                    "for ${tableName.namespace}.${tableName.name} to $s3Path"
            }

            fireboltClient.uploadToS3(s3Config.s3BucketName, s3Key, csvBytes)

            fireboltClient.copyFromS3(
                tableName = tableName,
                s3Path = s3Path,
                accessKeyId = s3Config.accessKeyId,
                secretAccessKey = s3Config.secretAccessKey,
            )

            log.info { "Loaded data into ${tableName.namespace}.${tableName.name}" }

            if (purgeStagingData) {
                fireboltClient.deleteFromS3(s3Config.s3BucketName, s3Key)
                log.debug { "Purged staging file: $s3Key" }
            }
        } catch (e: Exception) {
            log.error(e) {
                "Failed to flush $recordCount record(s) for " +
                    "${tableName.namespace}.${tableName.name}"
            }
            throw e
        } finally {
            resetState()
        }
    }

    private fun initializeBuffer() {
        val buffer = ByteArrayOutputStream()
        val gzip = CompressionOutputStream(buffer)
        val writer = csvWriterBuilder.build(gzip)
        writer.writeRecord(columns)
        byteBuffer = buffer
        gzipOutputStream = gzip
        csvWriter = writer
    }

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

    private fun resolveFileName(): String {
        val pattern = s3Config.fileNamePattern
        if (pattern.isNullOrBlank()) {
            val timestamp = Instant.now().toEpochMilli()
            val uniqueId = UUID.randomUUID().toString().replace("-", "").take(8)
            return "${timestamp}_$uniqueId$STAGING_FILE_EXTENSION"
        }

        val millis = Instant.now().toEpochMilli()
        var resolved = pattern.trim().replace(" ", "_")

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

        val defaultDateFmt =
            SimpleDateFormat(DATE_FORMAT).apply { timeZone = TimeZone.getTimeZone(UTC) }
        resolved =
            resolved
                .replace("{date}", defaultDateFmt.format(millis))
                .replace("{timestamp}", millis.toString())
                .replace("{sync_id}", System.getenv("WORKER_JOB_ID") ?: "")
                .replace("{format_extension}", STAGING_FILE_EXTENSION)
                .replace("{part_number}", partNumber.toString())

        if (!resolved.endsWith(STAGING_FILE_EXTENSION)) {
            resolved += STAGING_FILE_EXTENSION
        }

        return resolved
    }

    private fun resetState() {
        csvWriter = null
        gzipOutputStream = null
        byteBuffer = null
        recordCount = 0
    }
}

private class CompressionOutputStream(
    out: OutputStream,
    bufferSize: Int = 65_536,
) : GZIPOutputStream(out, bufferSize) {
    init {
        def.setLevel(5)
    }
}
