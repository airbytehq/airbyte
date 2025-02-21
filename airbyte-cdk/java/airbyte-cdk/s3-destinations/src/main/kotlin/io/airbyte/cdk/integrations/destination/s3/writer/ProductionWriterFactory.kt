/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.writer

import com.amazonaws.services.s3.AmazonS3
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.avro.AvroRecordFactory
import io.airbyte.cdk.integrations.destination.s3.avro.JsonToAvroSchemaConverter
import io.airbyte.cdk.integrations.destination.s3.avro.S3AvroWriter
import io.airbyte.cdk.integrations.destination.s3.csv.S3CsvWriter
import io.airbyte.cdk.integrations.destination.s3.jsonl.S3JsonlWriter
import io.airbyte.cdk.integrations.destination.s3.parquet.S3ParquetWriter
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Timestamp

private val LOGGER = KotlinLogging.logger {}

class ProductionWriterFactory : S3WriterFactory {
    @Throws(Exception::class)
    override fun create(
        config: S3DestinationConfig,
        s3Client: AmazonS3,
        configuredStream: ConfiguredAirbyteStream,
        uploadTimestamp: Timestamp
    ): DestinationFileWriter {
        val format = config.formatConfig!!.format

        if (format == FileUploadFormat.AVRO || format == FileUploadFormat.PARQUET) {
            val stream = configuredStream.stream
            LOGGER.info { "Json schema for stream ${stream.name}: ${stream.jsonSchema}" }

            val schemaConverter = JsonToAvroSchemaConverter()
            val avroSchema =
                schemaConverter.getAvroSchema(stream.jsonSchema, stream.name, stream.namespace)

            LOGGER.info {
                "Avro schema for stream ${stream.name}: ${@Suppress("DEPRECATION")avroSchema.toString(false)}"
            }

            return if (format == FileUploadFormat.AVRO) {
                S3AvroWriter(
                    config,
                    s3Client,
                    configuredStream,
                    uploadTimestamp,
                    avroSchema,
                    AvroRecordFactory.createV1JsonToAvroConverter()
                )
            } else {
                S3ParquetWriter(
                    config,
                    s3Client,
                    configuredStream,
                    uploadTimestamp,
                    avroSchema,
                    AvroRecordFactory.createV1JsonToAvroConverter()
                )
            }
        }

        if (format == FileUploadFormat.CSV) {
            return S3CsvWriter.Builder(config, s3Client, configuredStream, uploadTimestamp).build()
        }

        if (format == FileUploadFormat.JSONL) {
            return S3JsonlWriter(config, s3Client, configuredStream, uploadTimestamp)
        }

        throw RuntimeException("Unexpected S3 destination format: $format")
    }

    companion object {}
}
