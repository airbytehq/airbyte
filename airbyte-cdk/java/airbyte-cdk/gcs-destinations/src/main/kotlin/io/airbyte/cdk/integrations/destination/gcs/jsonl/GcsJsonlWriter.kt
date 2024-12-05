/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.jsonl

import alex.mojaki.s3upload.MultiPartOutputStream
import alex.mojaki.s3upload.StreamTransferManager
import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.writer.BaseGcsWriter
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory.create
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

class GcsJsonlWriter(
    config: GcsDestinationConfig,
    s3Client: AmazonS3,
    configuredStream: ConfiguredAirbyteStream,
    uploadTimestamp: Timestamp
) : BaseGcsWriter(config, s3Client, configuredStream), DestinationFileWriter {
    private val uploadManager: StreamTransferManager
    private val outputStream: MultiPartOutputStream
    private val printWriter: PrintWriter
    override val fileLocation: String
    override val outputPath: String

    init {
        val outputFilename: String =
            BaseGcsWriter.Companion.getOutputFilename(uploadTimestamp, FileUploadFormat.JSONL)
        outputPath = java.lang.String.join("/", outputPrefix, outputFilename)

        fileLocation = String.format("gs://%s/%s", config.bucketName, outputPath)
        LOGGER.info {
            "Full GCS path for stream '${stream.name}': ${config.bucketName}/$outputPath"
        }

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

    @Throws(IOException::class)
    override fun write(formattedData: JsonNode) {
        printWriter.println(Jsons.serialize(formattedData))
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

    companion object {

        private val MAPPER: ObjectMapper = MoreMappers.initMapper()
    }
}
