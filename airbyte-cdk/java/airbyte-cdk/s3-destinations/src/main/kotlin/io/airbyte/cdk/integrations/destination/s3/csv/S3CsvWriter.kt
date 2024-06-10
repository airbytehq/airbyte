/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.csv

import alex.mojaki.s3upload.MultiPartOutputStream
import alex.mojaki.s3upload.StreamTransferManager
import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.template.S3FilenameTemplateParameterObject.Companion.builder
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory.create
import io.airbyte.cdk.integrations.destination.s3.writer.BaseS3Writer
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

class S3CsvWriter
private constructor(
    config: S3DestinationConfig,
    s3Client: AmazonS3,
    configuredStream: ConfiguredAirbyteStream,
    uploadTimestamp: Timestamp,
    uploadThreads: Int,
    queueCapacity: Int,
    writeHeader: Boolean,
    csvSettings: CSVFormat,
    csvSheetGenerator: CsvSheetGenerator
) : BaseS3Writer(config, s3Client, configuredStream), DestinationFileWriter {
    private val csvSheetGenerator: CsvSheetGenerator
    private val uploadManager: StreamTransferManager
    private val outputStream: MultiPartOutputStream
    private val csvPrinter: CSVPrinter
    override val outputPath: String
    override val fileLocation: String

    init {
        var localCsvSettings = csvSettings
        this.csvSheetGenerator = csvSheetGenerator

        val fileSuffix = "_" + UUID.randomUUID()
        val outputFilename: String =
            BaseS3Writer.Companion.determineOutputFilename(
                builder()
                    .customSuffix(fileSuffix)
                    .s3Format(FileUploadFormat.CSV)
                    .fileExtension(FileUploadFormat.CSV.fileExtension)
                    .fileNamePattern(config.fileNamePattern)
                    .timestamp(uploadTimestamp)
                    .build()
            )
        this.outputPath = java.lang.String.join("/", outputPrefix, outputFilename)

        LOGGER.info {
            "Full S3 path for stream '${stream.name}': s3://${config.bucketName}/$outputPath"
        }
        fileLocation = String.format("gs://%s/%s", config.bucketName, outputPath)

        this.uploadManager =
            create(config.bucketName, outputPath, s3Client)
                .get()
                .numUploadThreads(uploadThreads)
                .queueCapacity(queueCapacity)
        // We only need one output stream as we only have one input stream. This is reasonably
        // performant.
        this.outputStream = uploadManager.multiPartOutputStreams[0]
        if (writeHeader) {
            localCsvSettings =
                @Suppress("deprecation")
                localCsvSettings.withHeader(
                    *csvSheetGenerator.getHeaderRow().toTypedArray<String>()
                )
        }
        this.csvPrinter =
            CSVPrinter(PrintWriter(outputStream, true, StandardCharsets.UTF_8), localCsvSettings)
    }

    class Builder(
        private val config: S3DestinationConfig,
        private val s3Client: AmazonS3,
        private val configuredStream: ConfiguredAirbyteStream,
        private val uploadTimestamp: Timestamp
    ) {
        private var uploadThreads = StreamTransferManagerFactory.DEFAULT_UPLOAD_THREADS
        private var queueCapacity = StreamTransferManagerFactory.DEFAULT_QUEUE_CAPACITY
        private var withHeader = true
        private var csvSettings: CSVFormat =
            @Suppress("deprecation") CSVFormat.DEFAULT.withQuoteMode(QuoteMode.ALL)
        private lateinit var _csvSheetGenerator: CsvSheetGenerator

        fun uploadThreads(uploadThreads: Int): Builder {
            this.uploadThreads = uploadThreads
            return this
        }

        fun queueCapacity(queueCapacity: Int): Builder {
            this.queueCapacity = queueCapacity
            return this
        }

        fun withHeader(withHeader: Boolean): Builder {
            this.withHeader = withHeader
            return this
        }

        fun csvSettings(csvSettings: CSVFormat): Builder {
            this.csvSettings = csvSettings
            return this
        }

        fun csvSheetGenerator(csvSheetGenerator: CsvSheetGenerator): Builder {
            this._csvSheetGenerator = csvSheetGenerator
            return this
        }

        @Throws(IOException::class)
        fun build(): S3CsvWriter {
            if (!::_csvSheetGenerator.isInitialized) {
                val formatConfig = config.formatConfig as UploadCsvFormatConfig
                _csvSheetGenerator =
                    CsvSheetGenerator.Factory.create(
                        configuredStream.stream.jsonSchema,
                        formatConfig
                    )
            }
            return S3CsvWriter(
                config,
                s3Client,
                configuredStream,
                uploadTimestamp,
                uploadThreads,
                queueCapacity,
                withHeader,
                csvSettings,
                _csvSheetGenerator
            )
        }
    }

    @Throws(IOException::class)
    override fun write(id: UUID, recordMessage: AirbyteRecordMessage) {
        csvPrinter.printRecord(csvSheetGenerator.getDataRow(id, recordMessage))
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

    @Throws(IOException::class)
    override fun write(formattedData: JsonNode) {
        csvPrinter.printRecord(csvSheetGenerator.getDataRow(formattedData))
    }

    companion object {}
}
