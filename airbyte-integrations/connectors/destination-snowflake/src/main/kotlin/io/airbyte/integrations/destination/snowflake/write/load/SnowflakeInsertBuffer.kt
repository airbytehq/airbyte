/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.QUOTE
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.io.OutputStream
import java.util.Random
import java.util.zip.GZIPOutputStream
import org.apache.commons.text.StringEscapeUtils

private val logger = KotlinLogging.logger {}

internal const val CSV_FILE_EXTENSION = ".csv"
internal const val CSV_FIELD_SEPARATOR = ","
internal const val CSV_LINE_DELIMITER = "\n"
internal const val FILE_PREFIX = "snowflake"
internal const val FILE_SUFFIX = ".csv"

class SnowflakeInsertBuffer(
    private val tableName: TableName,
    val columns: LinkedHashMap<String, String>,
    private val snowflakeClient: SnowflakeAirbyteClient,
    val snowflakeConfiguration: SnowflakeConfiguration,
    val snowflakeColumnUtils: SnowflakeColumnUtils,
) {

    @VisibleForTesting internal var recordCount = 0

    @VisibleForTesting internal val buffer: InputOutputBuffer = InputOutputBuffer()

    private val outputStream: CompressionOutputStream = CompressionOutputStream(buffer, 5)

    private val random: Random = Random()

    private val snowflakeRecordFormatter: SnowflakeRecordFormatter =
        when (snowflakeConfiguration.legacyRawTablesOnly) {
            true -> SnowflakeRawRecordFormatter(columns, snowflakeColumnUtils)
            else -> SnowflakeSchemaRecordFormatter(columns, snowflakeColumnUtils)
        }

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        bufferCsvRecord(recordFields)
    }

    suspend fun flush() =
        try {
            logger.info { "Beginning insert into ${tableName.toPrettyString(quote = QUOTE)}" }
            val fileName = generateFileName()

            val inputStream = getInputStream(buffer)

            inputStream.use {
                snowflakeClient.uploadToStage(
                    tableName = tableName,
                    inputStream = inputStream,
                    fileName = fileName,
                    compressData = false,
                )
            }
            snowflakeClient.copyFromStage(tableName, fileName)
            logger.info {
                "Finished insert of $recordCount row(s) into ${tableName.toPrettyString(quote = QUOTE)}"
            }
        } catch (e: Exception) {
            logger.error(e) { "Unable to flush accumulated data." }
            throw e
        }

    private fun bufferCsvRecord(record: Map<String, AirbyteValue>) {
        val formattedRecordValues = snowflakeRecordFormatter.format(record)
        formattedRecordValues.forEachIndexed { i, value ->
            val escapedValue =
                when (value) {
                    is String -> StringEscapeUtils.escapeCsv(value)
                    else -> value.toString()
                }
            outputStream.write(escapedValue.toByteArray())

            val lastBytes =
                if (i != formattedRecordValues.lastIndex) {
                    CSV_FIELD_SEPARATOR.toByteArray()
                } else {
                    CSV_LINE_DELIMITER.toByteArray()
                }
            outputStream.write(lastBytes)
        }
        recordCount++
    }

    private fun generateFileName() =
        "$FILE_PREFIX${java.lang.Long.toUnsignedString(random.nextLong())}$CSV_FILE_EXTENSION$FILE_SUFFIX"

    @VisibleForTesting
    internal fun getInputStream(buffer: InputOutputBuffer): InputStream {
        // Flush and close the GZIP output stream to finalize the compressed contents
        outputStream.flush()
        outputStream.close()
        return buffer.toInputStream()
    }

    internal class InputOutputBuffer : ByteArrayOutputStream() {
        fun toInputStream(): InputStream {
            flush()
            return ByteArrayInputStream(this.buf, 0, this.count)
        }
    }

    private class CompressionOutputStream(outputStream: OutputStream, level: Int) :
        GZIPOutputStream(outputStream) {
        init {
            def.setLevel(level)
        }
    }
}
