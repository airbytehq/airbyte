/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.csv

import alex.mojaki.s3upload.MultiPartOutputStream
import alex.mojaki.s3upload.StreamTransferManager
import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.writer.BaseGcsWriter
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSheetGenerator
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSheetGenerator.Factory.create
import io.airbyte.cdk.integrations.destination.s3.csv.UploadCsvFormatConfig
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory.create
import io.airbyte.cdk.integrations.destination.s3.writer.DestinationFileWriter
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.Timestamp
import java.util.*
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter
import org.apache.commons.csv.QuoteMode

private val LOGGER = KotlinLogging.logger {}

class GcsCsvWriter(
    config: GcsDestinationConfig,
    s3Client: AmazonS3,
    configuredStream: ConfiguredAirbyteStream,
    uploadTimestamp: Timestamp
) : BaseGcsWriter(config, s3Client, configuredStream), DestinationFileWriter {
    private val csvSheetGenerator: CsvSheetGenerator
    private val uploadManager: StreamTransferManager
    private val outputStream: MultiPartOutputStream
    val csvPrinter: CSVPrinter
    override val fileLocation: String
    override val outputPath: String

    init {
        val formatConfig = config.formatConfig as UploadCsvFormatConfig
        this.csvSheetGenerator = create(configuredStream.stream.jsonSchema, formatConfig)

        val outputFilename: String =
            BaseGcsWriter.Companion.getOutputFilename(uploadTimestamp, FileUploadFormat.CSV)
        outputPath = java.lang.String.join("/", outputPrefix, outputFilename)
        fileLocation = String.format("gs://%s/%s", config.bucketName, outputPath)

        LOGGER.info {
            "Full GCS path for stream '${stream.name}': ${config.bucketName}/$outputPath"
        }

        this.uploadManager =
            create(config.bucketName, outputPath, s3Client)
                .setPartSize(StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB.toLong())
                .get()
        // We only need one output stream as we only have one input stream. This is reasonably
        // performant.
        this.outputStream = uploadManager.multiPartOutputStreams[0]
        this.csvPrinter =
            CSVPrinter(
                PrintWriter(outputStream, true, StandardCharsets.UTF_8),
                @Suppress("deprecation")
                CSVFormat.DEFAULT.withQuoteMode(QuoteMode.ALL)
                    .withHeader(*csvSheetGenerator.getHeaderRow().toTypedArray<String>())
            )
    }

    @Throws(IOException::class)
    override fun write(id: UUID, recordMessage: AirbyteRecordMessage) {
        csvPrinter.printRecord(csvSheetGenerator.getDataRow(id, recordMessage))
    }

    @Throws(IOException::class)
    override fun write(formattedData: JsonNode) {
        csvPrinter.printRecord(csvSheetGenerator.getDataRow(formattedData))
    }

    @Throws(IOException::class)
    override fun closeWhenSucceed() {
        csvPrinter.close()
        outputStream.close()
        uploadManager.complete()
    }

    @Throws(IOException::class)
    override fun closeWhenFail() {
        csvPrinter.close()
        outputStream.close()
        uploadManager.abort()
    }

    override val fileFormat: FileUploadFormat
        get() = FileUploadFormat.CSV

    companion object {}
}
