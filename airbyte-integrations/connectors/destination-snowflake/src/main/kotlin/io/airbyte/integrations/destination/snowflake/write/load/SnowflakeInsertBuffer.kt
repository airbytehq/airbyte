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
import java.util.Random
import java.util.zip.GZIPOutputStream
import org.apache.commons.text.StringEscapeUtils

private val logger = KotlinLogging.logger {}

internal const val CSV_FIELD_SEPARATOR = ","
internal const val CSV_LINE_DELIMITER = "\n"

class SnowflakeInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val snowflakeClient: SnowflakeAirbyteClient,
    val snowflakeConfiguration: SnowflakeConfiguration,
    val snowflakeColumnUtils: SnowflakeColumnUtils,
) {

    @VisibleForTesting internal var recordCount = 0

    @VisibleForTesting internal var buffer: ByteArrayOutputStream? = null

    private lateinit var outputStream: GZIPOutputStream

    private val random: Random = Random()

    private val snowflakeRecordFormatter: SnowflakeRecordFormatter =
        when (snowflakeConfiguration.legacyRawTablesOnly) {
            true -> SnowflakeRawRecordFormatter(columns, snowflakeColumnUtils)
            else -> SnowflakeSchemaRecordFormatter(columns, snowflakeColumnUtils)
        }

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (buffer == null) {
            buffer = ByteArrayOutputStream()
            outputStream = GZIPOutputStream(buffer)
        }
        bufferCsvRecord(recordFields)
    }

    suspend fun flush() =
        buffer?.let { b ->
            try {
                logger.info { "Beginning insert into ${tableName.toPrettyString(quote = QUOTE)}" }
                val fileName =
                    "snowflake${java.lang.Long.toUnsignedString(random.nextLong())}.csv.gz"

                val inputStream = getInputStream(b)

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
            } finally {
                buffer?.close()
                buffer = null
                recordCount = 0
            }
        }
            ?: logger.warn { "Buffer is null: nothing to flush." }

    private fun bufferCsvRecord(record: Map<String, AirbyteValue>) {
        buffer?.let { b ->
            val line =
                snowflakeRecordFormatter.format(record).joinToString(
                    separator = CSV_FIELD_SEPARATOR,
                    postfix = CSV_LINE_DELIMITER
                ) { col ->
                    when (col) {
                        is String -> StringEscapeUtils.escapeCsv(col)
                        else -> col.toString()
                    }
                }
            outputStream.write(line.toByteArray())
            recordCount++
        }
    }

    @VisibleForTesting
    internal fun getInputStream(buffer: ByteArrayOutputStream): InputStream {
        // Flush and close the GZIP output stream to finalize the compressed contents
        outputStream.flush()
        outputStream.close()
        return ByteArrayInputStream(buffer.toByteArray())
    }
}
