/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import com.google.common.annotations.VisibleForTesting
import de.siegmar.fastcsv.writer.CsvWriter
import de.siegmar.fastcsv.writer.LineDelimiter
import de.siegmar.fastcsv.writer.QuoteStrategies
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.QUOTE
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.OutputStream
import java.nio.file.Path
import java.util.zip.GZIPOutputStream
import kotlin.io.path.deleteIfExists
import kotlin.io.path.pathString

private val logger = KotlinLogging.logger {}

internal const val CSV_FILE_EXTENSION = ".csv"
internal const val CSV_FIELD_SEPARATOR = ','
internal const val CSV_QUOTE_CHARACTER = '"'
internal val CSV_LINE_DELIMITER = LineDelimiter.LF
internal const val DEFAULT_FLUSH_LIMIT = 1000
internal const val FILE_PREFIX = "snowflake"
internal const val FILE_SUFFIX = ".gz"

private const val CSV_WRITER_BUFFER_SIZE = 1024 * 1024 // 1 MB

class SnowflakeInsertBuffer(
    private val tableName: TableName,
    private val snowflakeClient: SnowflakeAirbyteClient,
    val snowflakeConfiguration: SnowflakeConfiguration,
    val columnSchema: ColumnSchema,
    private val columnManager: SnowflakeColumnManager,
    private val snowflakeRecordFormatter: SnowflakeRecordFormatter,
    private val flushLimit: Int = DEFAULT_FLUSH_LIMIT,
) {

    @VisibleForTesting internal var csvFilePath: Path? = null

    @VisibleForTesting internal var recordCount = 0

    @VisibleForTesting internal var csvWriter: CsvWriter? = null

    private val csvWriterBuilder =
        CsvWriter.builder()
            .bufferSize(CSV_WRITER_BUFFER_SIZE)
            .fieldSeparator(CSV_FIELD_SEPARATOR)
            .quoteCharacter(CSV_QUOTE_CHARACTER)
            .lineDelimiter(CSV_LINE_DELIMITER)
            .quoteStrategy(QuoteStrategies.REQUIRED)

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (csvFilePath == null) {
            val csvFile = createCsvFile()
            csvFilePath = csvFile.toPath()
            csvWriter =
                csvWriterBuilder.build(
                    CompressionOutputStream(outputStream = csvFile.outputStream(), level = 5)
                )
        }

        writeToCsvFile(recordFields)
    }

    suspend fun flush() {
        csvFilePath?.let { filePath ->
            try {
                // Flush and close the CSV write to ensure that any pending writes are written
                // to the file AND that any proper end of file markers are written by the close
                csvWriter?.flush()
                csvWriter?.close()
                logger.info {
                    "Beginning insert into ${tableName.toPrettyString(quote = QUOTE)}..."
                }
                // Next, put the CSV file into the staging table
                snowflakeClient.putInStage(tableName, filePath.pathString)
                logger.info {
                    "Copying staging data into ${tableName.toPrettyString(quote = QUOTE)}..."
                }
                // Finally, copy the data from the staging table to the final table
                // Pass column names to ensure correct mapping even after ALTER TABLE operations
                val columnNames = columnManager.getTableColumnNames(columnSchema)
                snowflakeClient.copyFromStage(tableName, filePath.fileName.toString(), columnNames)
                logger.info {
                    "Finished insert of $recordCount row(s) into ${tableName.toPrettyString(quote = QUOTE)}."
                }
            } catch (e: Exception) {
                logger.error(e) { "Unable to flush accumulated data." }
                throw e
            } finally {
                filePath.deleteIfExists()
                csvWriter = null
                csvFilePath = null
                recordCount = 0
            }
        }
            ?: logger.warn { "CSV file path is not set: nothing to upload to staging." }
    }

    private fun createCsvFile(): File {
        val csvFile = File.createTempFile(FILE_PREFIX, "$CSV_FILE_EXTENSION$FILE_SUFFIX")
        csvFile.deleteOnExit()
        return csvFile
    }

    private fun writeToCsvFile(record: Map<String, AirbyteValue>) {
        csvWriter?.let {
            it.writeRecord(
                snowflakeRecordFormatter.format(record, columnSchema).map { col -> col.toString() }
            )
            recordCount++
            if ((recordCount % flushLimit) == 0) {
                it.flush()
            }
        }
    }

    private class CompressionOutputStream(outputStream: OutputStream, level: Int) :
        GZIPOutputStream(outputStream) {
        init {
            def.setLevel(level)
        }
    }
}
