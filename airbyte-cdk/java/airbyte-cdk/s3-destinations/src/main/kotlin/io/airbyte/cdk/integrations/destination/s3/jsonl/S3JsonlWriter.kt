/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.jsonl

import alex.mojaki.s3upload.MultiPartOutputStream
import alex.mojaki.s3upload.StreamTransferManager
import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.template.S3FilenameTemplateParameterObject.Companion.builder
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory.create
import io.airbyte.cdk.integrations.destination.s3.writer.BaseS3Writer
import io.airbyte.cdk.integrations.destination.s3.writer.DestinationFileWriter
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.Timestamp
import java.util.*

private val LOGGER = KotlinLogging.logger {}

class S3JsonlWriter(
    config: S3DestinationConfig,
    s3Client: AmazonS3,
    configuredStream: ConfiguredAirbyteStream,
    uploadTimestamp: Timestamp?
) : BaseS3Writer(config, s3Client, configuredStream), DestinationFileWriter {
    private val uploadManager: StreamTransferManager
    private val outputStream: MultiPartOutputStream
    private val printWriter: PrintWriter
    override val outputPath: String
    override val fileLocation: String

    init {
        val outputFilename: String =
            BaseS3Writer.Companion.determineOutputFilename(
                builder()
                    .timestamp(uploadTimestamp)
                    .s3Format(FileUploadFormat.JSONL)
                    .fileExtension(FileUploadFormat.JSONL.fileExtension)
                    .fileNamePattern(config.fileNamePattern)
                    .build()
            )
        outputPath = java.lang.String.join("/", outputPrefix, outputFilename)

        LOGGER.info {
            "Full S3 path for stream '${stream.name}': s3://${config.bucketName}/$outputPath"
        }
        fileLocation = String.format("gs://%s/%s", config.bucketName, outputPath)

        this.uploadManager = create(config.bucketName, outputPath, s3Client).get()
        // We only need one output stream as we only have one input stream. This is reasonably
        // performant.
        this.outputStream = uploadManager.multiPartOutputStreams[0]
        this.printWriter = PrintWriter(outputStream, true, StandardCharsets.UTF_8)
    }

    override fun write(id: UUID, recordMessage: AirbyteRecordMessage) {
        val json = MAPPER.createObjectNode()
        json.put(JavaBaseConstants.COLUMN_NAME_AB_ID, id.toString())
        json.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.emittedAt)
        json.set<JsonNode>(JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.data)
        printWriter.println(Jsons.serialize(json))
    }

    override fun closeWhenSucceed() {
        printWriter.close()
        outputStream.close()
        uploadManager.complete()
    }

    override fun closeWhenFail() {
        printWriter.close()
        outputStream.close()
        uploadManager.abort()
    }

    override val fileFormat: FileUploadFormat
        get() = FileUploadFormat.JSONL

    @Throws(IOException::class)
    override fun write(formattedData: JsonNode) {
        printWriter.println(Jsons.serialize(formattedData))
    }

    companion object {

        private val MAPPER: ObjectMapper = MoreMappers.initMapper()
    }
}
