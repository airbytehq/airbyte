/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.parquet

import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.avro.AvroRecordFactory
import io.airbyte.cdk.integrations.destination.s3.credential.S3AccessKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.template.S3FilenameTemplateParameterObject.Companion.builder
import io.airbyte.cdk.integrations.destination.s3.writer.BaseS3Writer
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
import org.apache.hadoop.fs.s3a.Constants
import org.apache.parquet.avro.AvroParquetWriter
import org.apache.parquet.avro.AvroWriteSupport
import org.apache.parquet.hadoop.ParquetWriter
import org.apache.parquet.hadoop.util.HadoopOutputFile
import tech.allegro.schema.json2avro.converter.JsonAvroConverter

private val LOGGER = KotlinLogging.logger {}

class S3ParquetWriter(
    config: S3DestinationConfig,
    s3Client: AmazonS3,
    configuredStream: ConfiguredAirbyteStream,
    uploadTimestamp: Timestamp?,
    schema: Schema?,
    converter: JsonAvroConverter?
) : BaseS3Writer(config, s3Client, configuredStream), DestinationFileWriter {
    private val parquetWriter: ParquetWriter<GenericData.Record>
    private val avroRecordFactory: AvroRecordFactory
    val schema: Schema?
    private val outputFilename: String =
        determineOutputFilename(
            builder()
                .s3Format(FileUploadFormat.PARQUET)
                .timestamp(uploadTimestamp)
                .fileExtension(FileUploadFormat.PARQUET.fileExtension)
                .fileNamePattern(config.fileNamePattern)
                .build()
        )

    // object key = <path>/<output-filename>
    override val outputPath: String = java.lang.String.join("/", outputPrefix, outputFilename)

    // full file path = s3://<bucket>/<path>/<output-filename>
    override val fileLocation: String = String.format("s3a://%s/%s", config.bucketName, outputPath)

    init {
        LOGGER.info { "Full S3 path for stream '${stream.name}': $fileLocation" }

        val path = Path(URI(fileLocation))
        val formatConfig = config.formatConfig as UploadParquetFormatConfig
        val hadoopConfig = getHadoopConfig(config)
        hadoopConfig.setBoolean(AvroWriteSupport.WRITE_OLD_LIST_STRUCTURE, false)
        this.parquetWriter =
            AvroParquetWriter.builder<GenericData.Record>(
                    HadoopOutputFile.fromPath(path, hadoopConfig)
                )
                .withConf(
                    hadoopConfig
                ) // yes, this should be here despite the fact we pass this config above in path
                .withSchema(schema)
                .withCompressionCodec(formatConfig.compressionCodec)
                .withRowGroupSize(formatConfig.blockSize.toLong())
                .withMaxPaddingSize(formatConfig.maxPaddingSize)
                .withPageSize(formatConfig.pageSize)
                .withDictionaryPageSize(formatConfig.dictionaryPageSize)
                .withDictionaryEncoding(formatConfig.isDictionaryEncoding)
                .build()
        this.avroRecordFactory = AvroRecordFactory(schema, converter)
        this.schema = schema
    }

    val outputFilePath: String
        /** The file path includes prefix and filename, but does not include the bucket name. */
        get() = "$outputPrefix/$outputFilename"

    @Throws(IOException::class)
    override fun write(id: UUID, recordMessage: AirbyteRecordMessage) {
        parquetWriter.write(avroRecordFactory.getAvroRecord(id, recordMessage))
    }

    @Throws(IOException::class)
    override fun closeWhenSucceed() {
        parquetWriter.close()
    }

    @Throws(IOException::class)
    override fun closeWhenFail() {
        parquetWriter.close()
    }

    override val fileFormat: FileUploadFormat
        get() = FileUploadFormat.PARQUET

    @Throws(IOException::class)
    override fun write(formattedData: JsonNode) {
        parquetWriter.write(avroRecordFactory.getAvroRecord(formattedData))
    }

    companion object {

        @JvmStatic
        fun getHadoopConfig(config: S3DestinationConfig): Configuration {
            val hadoopConfig = Configuration()
            val credentialConfig = config.s3CredentialConfig as S3AccessKeyCredentialConfig
            hadoopConfig[Constants.ACCESS_KEY] = credentialConfig.accessKeyId
            hadoopConfig[Constants.SECRET_KEY] = credentialConfig.secretAccessKey
            if (config.endpoint.isNullOrEmpty()) {
                hadoopConfig[Constants.ENDPOINT] =
                    String.format("s3.%s.amazonaws.com", config.bucketRegion)
            } else {
                hadoopConfig[Constants.ENDPOINT] = config.endpoint
                hadoopConfig[Constants.PATH_STYLE_ACCESS] = "true"
            }
            hadoopConfig[Constants.AWS_CREDENTIALS_PROVIDER] =
                "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
            return hadoopConfig
        }
    }
}
