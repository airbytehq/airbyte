/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.load

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.nio.file.Path
import kotlin.io.path.deleteIfExists
import kotlin.io.path.pathString
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

private val logger = KotlinLogging.logger {}

internal val CSV_FORMAT = CSVFormat.DEFAULT
internal const val DEFAULT_FLUSH_LIMIT = 1000

class PostgresInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val postgresClient: PostgresAirbyteClient,
    val postgresConfiguration: PostgresConfiguration,
    private val flushLimit: Int = DEFAULT_FLUSH_LIMIT,
) {

    @VisibleForTesting internal var csvFilePath: Path? = null

    @VisibleForTesting internal var recordCount = 0

    private var csvPrinter: CSVPrinter? = null

    private val postgresRecordFormatter: PostgresRecordFormatter =
        when (postgresConfiguration.legacyRawTablesOnly) {
            true -> PostgresRawRecordFormatter(columns)
            else -> PostgresSchemaRecordFormatter(columns)
        }

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (csvFilePath == null) {
            val csvFile = createCsvFile()
            csvFilePath = csvFile.toPath()
            csvPrinter = CSVPrinter(csvFile.bufferedWriter(Charsets.UTF_8), CSV_FORMAT)
        }

        writeToCsvFile(recordFields)
    }

    suspend fun flush() {
        csvFilePath?.let { filePath ->
            try {
                csvPrinter?.flush()
                logger.info { "Beginning insert into ${tableName.namespace}.${tableName.name}" }
                // Copy the data from the CSV file into the table using COPY command
                postgresClient.copyFromCsv(tableName, filePath.pathString)
                logger.info {
                    "Finished insert of $recordCount row(s) into ${tableName.namespace}.${tableName.name}"
                }
            } catch (e: Exception) {
                logger.error(e) { "Unable to flush accumulated data." }
            } finally {
                filePath.deleteIfExists()
                csvPrinter?.close()
                csvPrinter = null
                csvFilePath = null
                recordCount = 0
            }
        }
            ?: logger.warn { "CSV file path is not set: nothing to upload." }
    }

    private fun createCsvFile(): File {
        val csvFile = File.createTempFile("postgres", ".csv")
        csvFile.deleteOnExit()
        return csvFile
    }

    private fun writeToCsvFile(record: Map<String, AirbyteValue>) {
        csvPrinter?.let {
            it.printRecord(postgresRecordFormatter.format(record))
            recordCount++
            if ((recordCount % flushLimit) == 0) {
                it.flush()
            }
        }
    }
}
