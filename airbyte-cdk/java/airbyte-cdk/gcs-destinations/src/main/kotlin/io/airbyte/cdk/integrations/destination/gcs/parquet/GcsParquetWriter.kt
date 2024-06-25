/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.parquet

import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.gcs.util.GcsS3FileSystem
import io.airbyte.cdk.integrations.destination.gcs.writer.BaseGcsWriter
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.avro.AvroRecordFactory
import io.airbyte.cdk.integrations.destination.s3.parquet.UploadParquetFormatConfig
import io.airbyte.cdk.integrations.destination.s3.writer.DestinationFileWriter
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.net.URI
import java.sql.Timestamp
import java.util.*
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.Path
import org.apache.parquet.avro.AvroParquetWriter
import org.apache.parquet.hadoop.ParquetWriter
import org.apache.parquet.hadoop.util.HadoopOutputFile
import tech.allegro.schema.json2avro.converter.JsonAvroConverter

private val LOGGER = KotlinLogging.logger {}

class GcsParquetWriter(
    config: GcsDestinationConfig,
    s3Client: AmazonS3,
    configuredStream: ConfiguredAirbyteStream,
    uploadTimestamp: Timestamp,
    schema: Schema?,
    converter: JsonAvroConverter?
) : BaseGcsWriter(config, s3Client, configuredStream), DestinationFileWriter {
    private val parquetWriter: ParquetWriter<GenericData.Record>
    private val avroRecordFactory: AvroRecordFactory
    override val fileLocation: String
    override val outputPath: String

    init {
        val outputFilename: String =
            BaseGcsWriter.Companion.getOutputFilename(uploadTimestamp, FileUploadFormat.PARQUET)
        outputPath = java.lang.String.join("/", outputPrefix, outputFilename)
        LOGGER.info { "Storage path for stream '${stream.name}': ${config.bucketName}/$outputPath" }

        fileLocation =
            String.format("s3a://%s/%s/%s", config.bucketName, outputPrefix, outputFilename)
        val uri = URI(fileLocation)
        val path = Path(uri)

        LOGGER.info { "Full GCS path for stream '${stream.name}': $path" }

        val formatConfig = config.formatConfig as UploadParquetFormatConfig
        val hadoopConfig = getHadoopConfig(config)
        this.parquetWriter =
            @Suppress("deprecation")
            AvroParquetWriter.builder<GenericData.Record>(
                    HadoopOutputFile.fromPath(path, hadoopConfig)
                )
                .withSchema(schema)
                .withCompressionCodec(formatConfig.compressionCodec)
                .withRowGroupSize(formatConfig.blockSize)
                .withMaxPaddingSize(formatConfig.maxPaddingSize)
                .withPageSize(formatConfig.pageSize)
                .withDictionaryPageSize(formatConfig.dictionaryPageSize)
                .withDictionaryEncoding(formatConfig.isDictionaryEncoding)
                .build()
        this.avroRecordFactory = AvroRecordFactory(schema, converter)
    }

    @Throws(IOException::class)
    override fun write(id: UUID, recordMessage: AirbyteRecordMessage) {
        parquetWriter.write(avroRecordFactory.getAvroRecord(id, recordMessage))
    }

    @Throws(IOException::class)
    override fun write(formattedData: JsonNode) {
        parquetWriter.write(avroRecordFactory.getAvroRecord(formattedData))
    }

    @Throws(IOException::class)
    override fun close(hasFailed: Boolean) {
        if (hasFailed) {
            LOGGER.warn { "Failure detected. Aborting upload of stream '${stream.name}'..." }
            parquetWriter.close()
            LOGGER.warn { "Upload of stream '${stream.name}' aborted." }
        } else {
            LOGGER.info { "Uploading remaining data for stream '${stream.name}'." }
            parquetWriter.close()
            LOGGER.info { "Upload completed for stream '${stream.name}'." }
        }
    }

    override val fileFormat: FileUploadFormat
        get() = FileUploadFormat.PARQUET

    companion object {

        private val MAPPER = ObjectMapper()

        fun getHadoopConfig(config: GcsDestinationConfig): Configuration {
            val hmacKeyCredential = config.gcsCredentialConfig as GcsHmacKeyCredentialConfig
            val hadoopConfig = Configuration()

            // the default org.apache.hadoop.fs.s3a.S3AFileSystem does not work for GCS
            hadoopConfig["fs.s3a.impl"] = GcsS3FileSystem::class.java.canonicalName

            // https://stackoverflow.com/questions/64141204/process-data-in-google-storage-on-an-aws-emr-cluster-in-spark
            hadoopConfig["fs.s3a.access.key"] = hmacKeyCredential.hmacKeyAccessId
            hadoopConfig["fs.s3a.secret.key"] = hmacKeyCredential.hmacKeySecret
            hadoopConfig.setBoolean("fs.s3a.path.style.access", true)
            hadoopConfig["fs.s3a.endpoint"] = "storage.googleapis.com"
            hadoopConfig.setInt("fs.s3a.list.version", 1)

            return hadoopConfig
        }
    }
}
