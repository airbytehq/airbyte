/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.avro

import alex.mojaki.s3upload.MultiPartOutputStream
import alex.mojaki.s3upload.StreamTransferManager
import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.util.GcsUtils
import io.airbyte.cdk.integrations.destination.gcs.writer.BaseGcsWriter
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.avro.AvroRecordFactory
import io.airbyte.cdk.integrations.destination.s3.avro.JsonToAvroSchemaConverter
import io.airbyte.cdk.integrations.destination.s3.avro.UploadAvroFormatConfig
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory.create
import io.airbyte.cdk.integrations.destination.s3.writer.DestinationFileWriter
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.sql.Timestamp
import java.util.*
import org.apache.avro.file.DataFileWriter
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericDatumWriter
import tech.allegro.schema.json2avro.converter.JsonAvroConverter

private val LOGGER = KotlinLogging.logger {}

class GcsAvroWriter
@JvmOverloads
constructor(
    config: GcsDestinationConfig,
    s3Client: AmazonS3,
    configuredStream: ConfiguredAirbyteStream,
    uploadTimestamp: Timestamp,
    converter: JsonAvroConverter?,
    jsonSchema: JsonNode? = null
) : BaseGcsWriter(config, s3Client, configuredStream), DestinationFileWriter {
    private val avroRecordFactory: AvroRecordFactory
    private val uploadManager: StreamTransferManager
    private val outputStream: MultiPartOutputStream
    private val dataFileWriter: DataFileWriter<GenericData.Record>
    override val fileLocation: String
    override val outputPath: String

    init {
        val schema =
            if (jsonSchema == null)
                GcsUtils.getDefaultAvroSchema(stream.name, stream.namespace, true, false)
            else
                JsonToAvroSchemaConverter()
                    .getAvroSchema(
                        jsonSchema,
                        stream.name,
                        stream.namespace,
                        true,
                        false,
                        false,
                        true
                    )
        LOGGER.info {
            "Avro schema for stream ${stream.name}: ${@Suppress("DEPRECATION")schema!!.toString(false)}"
        }

        val outputFilename: String = getOutputFilename(uploadTimestamp, FileUploadFormat.AVRO)
        outputPath = java.lang.String.join("/", outputPrefix, outputFilename)
        fileLocation = String.format("gs://%s/%s", config.bucketName, outputPath)

        LOGGER.info {
            "Full GCS path for stream '${stream.name}': ${config.bucketName}/$outputPath"
        }

        this.avroRecordFactory = AvroRecordFactory(schema, converter)
        this.uploadManager =
            create(config.bucketName, outputPath, s3Client)
                .setPartSize(StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB.toLong())
                .get()
        // We only need one output stream as we only have one input stream. This is reasonably
        // performant.
        this.outputStream = uploadManager.multiPartOutputStreams[0]

        val formatConfig = config.formatConfig as UploadAvroFormatConfig
        // The DataFileWriter always uses binary encoding.
        // If json encoding is needed in the future, use the GenericDatumWriter directly.
        this.dataFileWriter =
            DataFileWriter(GenericDatumWriter<GenericData.Record>())
                .setCodec(formatConfig.codecFactory)
                .create(schema, outputStream)
    }

    @Throws(IOException::class)
    override fun write(id: UUID, recordMessage: AirbyteRecordMessage) {
        dataFileWriter.append(avroRecordFactory.getAvroRecord(id, recordMessage))
    }

    @Throws(IOException::class)
    override fun write(formattedData: JsonNode) {
        val record = avroRecordFactory.getAvroRecord(formattedData)
        dataFileWriter.append(record)
    }

    @Throws(IOException::class)
    override fun closeWhenSucceed() {
        dataFileWriter.close()
        outputStream.close()
        uploadManager.complete()
    }

    @Throws(IOException::class)
    override fun closeWhenFail() {
        dataFileWriter.close()
        outputStream.close()
        uploadManager.abort()
    }

    override val fileFormat: FileUploadFormat
        get() = FileUploadFormat.AVRO

    companion object {}
}
