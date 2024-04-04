package io.airbyte.integrations.destination.s3.buffer

import io.airbyte.cdk.core.config.AirbyteConfiguredCatalog
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.S3Format
import io.airbyte.cdk.integrations.destination.s3.avro.AvroSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.avro.JsonToAvroSchemaConverter
import io.airbyte.cdk.integrations.destination.s3.avro.S3AvroFormatConfig
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.csv.NoFlatteningSheetGenerator
import io.airbyte.cdk.integrations.destination.s3.csv.RootLevelFlatteningSheetGenerator
import io.airbyte.cdk.integrations.destination.s3.csv.S3CsvFormatConfig
import io.airbyte.cdk.integrations.destination.s3.jsonl.JsonLSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.jsonl.S3JsonlFormatConfig
import io.airbyte.cdk.integrations.destination.s3.parquet.S3ParquetFormatConfig
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.integrations.destination.s3.config.properties.S3ConnectorConfiguration
import io.airbyte.integrations.destination.s3.config.properties.S3ConnectorOutputFormat
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import org.apache.avro.file.CodecFactory
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.QuoteMode
import org.apache.commons.lang3.StringUtils

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
class SerializedBufferFactory(
    private val s3ConnectorConfiguration: S3ConnectorConfiguration,
    private val airbyteConfiguredCatalog: AirbyteConfiguredCatalog,
) {

    fun createSerializedBuffer(stream: StreamDescriptor): SerializableBuffer {
        val formatConfig = s3ConnectorConfiguration.getOutputFormat()
        formatConfig.formatType?.let { formatType ->
            val s3Format = S3Format.valueOf(formatType)
            val fileExtension = getFileExtension(s3Format, formatConfig)
            return when (s3Format) {
                S3Format.CSV -> createCsvSerializableBuffer(fileExtension, stream, formatConfig)
                S3Format.AVRO -> createAvroSerializableBuffer(fileExtension, stream, formatConfig)
                S3Format.JSONL -> createJsonLSerializableBuffer(fileExtension, formatConfig)
                S3Format.PARQUET -> createParquetSerializableBuffer(fileExtension, stream, formatConfig)
            }
        }

        throw IllegalArgumentException("Format type not provided.")
    }

    private fun getFileExtension(format: S3Format, formatConfig: S3ConnectorOutputFormat): String {
        val compressionType: CompressionType? = formatConfig.compression?.getCompressionType()
        return when(format) {
            S3Format.AVRO -> S3AvroFormatConfig.DEFAULT_SUFFIX
            S3Format.CSV -> S3CsvFormatConfig.CSV_SUFFIX + if(compressionType != null) { compressionType.fileExtension } else {
                S3DestinationConstants.DEFAULT_COMPRESSION_TYPE}
            S3Format.JSONL -> S3JsonlFormatConfig.JSONL_SUFFIX + if(compressionType != null) { compressionType.fileExtension } else {
                S3DestinationConstants.DEFAULT_COMPRESSION_TYPE}
            S3Format.PARQUET -> S3ParquetFormatConfig.PARQUET_SUFFIX
        }
    }

    private fun createAvroSerializableBuffer(fileExtension: String, stream: StreamDescriptor, formatConfig: S3ConnectorOutputFormat): SerializableBuffer {
        val codecFactory = createAvroCodecFactory(formatConfig)
        val schemaConverter = JsonToAvroSchemaConverter()
        val schema = schemaConverter.getAvroSchema(
            airbyteConfiguredCatalog.getConfiguredCatalog().streams
                .stream()
                .filter { s: ConfiguredAirbyteStream ->
                    s.stream.name == stream.name && StringUtils.equals(
                        s.stream.namespace,
                        stream.namespace
                    )
                }
                .findFirst()
                .orElseThrow {
                    RuntimeException(
                        String.format("No such stream %s.%s", stream.namespace, stream.name)
                    )
                }
                .stream
                .jsonSchema,
            stream.name, stream.namespace
        )
        return AvroSerializedBuffer(FileBuffer(fileExtension), codecFactory, schema)
    }

    private fun createAvroCodecFactory(formatConfig: S3ConnectorOutputFormat) : CodecFactory {
        return if (formatConfig.compressionCodec != null) {
            val compressionCodec = formatConfig.compressionCodec
            when (compressionCodec.getCodec()) {
                S3AvroFormatConfig.CompressionCodec.NULL -> CodecFactory.nullCodec()
                S3AvroFormatConfig.CompressionCodec.DEFLATE -> CodecFactory.deflateCodec(compressionCodec.getCompressionLevel(0,0,9))
                S3AvroFormatConfig.CompressionCodec.BZIP2 -> CodecFactory.bzip2Codec()
                S3AvroFormatConfig.CompressionCodec.XZ -> CodecFactory.xzCodec(compressionCodec.getCompressionLevel(6,0,9))
                S3AvroFormatConfig.CompressionCodec.ZSTANDARD -> CodecFactory.zstandardCodec(compressionCodec.getCompressionLevel(3, -5, 22), compressionCodec.includeChecksum)
                S3AvroFormatConfig.CompressionCodec.SNAPPY -> CodecFactory.snappyCodec()
            }
        } else {
            CodecFactory.nullCodec()
        }
    }

    private fun createCsvSerializableBuffer(fileExtension:String, stream: StreamDescriptor, formatConfig: S3ConnectorOutputFormat): SerializableBuffer {
        val schema = airbyteConfiguredCatalog.getConfiguredCatalog().streams
            .stream()
            .filter { s: ConfiguredAirbyteStream ->
                s.stream.name == stream.name && StringUtils.equals(s.stream.namespace, stream.namespace)
            }
            .findFirst()
            .orElseThrow {
                java.lang.RuntimeException(
                    String.format("No such stream %s.%s", stream.namespace, stream.name)
                )
            }
            .stream
            .jsonSchema
        val csvSheetGenerator = if(formatConfig.getFlattening() == Flattening.ROOT_LEVEL) {
            RootLevelFlatteningSheetGenerator(schema)
        } else {
            NoFlatteningSheetGenerator()
        }
        val csvSettings = CSVFormat.DEFAULT.builder().setQuoteMode(QuoteMode.NON_NUMERIC).setHeader(*csvSheetGenerator.headerRow.toTypedArray<String>()).build()
        val compression = formatConfig.compression?.getCompressionType() != CompressionType.NO_COMPRESSION
        return CsvSerializedBuffer(
            FileBuffer(fileExtension),
            csvSheetGenerator,
            compression
        ).withCsvFormat(csvSettings)
    }

    private fun createJsonLSerializableBuffer(fileExtension: String, formatConfig: S3ConnectorOutputFormat): SerializableBuffer {
        val compressionType = if(formatConfig.compression?.getCompressionType() == null) {
            S3DestinationConstants.DEFAULT_COMPRESSION_TYPE
        } else {
            formatConfig.compression.getCompressionType()
        }
        val flattening = formatConfig.getFlattening()
        return JsonLSerializedBuffer(
            FileBuffer(fileExtension),
            compressionType != CompressionType.NO_COMPRESSION,
            flattening != Flattening.NO
        )
    }

    private fun createParquetSerializableBuffer(fileExtension: String, stream: StreamDescriptor, formatConfig: S3ConnectorOutputFormat): SerializableBuffer {
        val schema = JsonToAvroSchemaConverter().getAvroSchema(airbyteConfiguredCatalog.getConfiguredCatalog().streams
            .stream()
            .filter { s: ConfiguredAirbyteStream ->
                s.stream.name == stream.name && StringUtils.equals(s.stream.namespace, stream.namespace)
            }
            .findFirst()
            .orElseThrow {
                RuntimeException(
                    String.format("No such stream %s.%s", stream.namespace, stream.name)
                )
            }
            .stream
            .jsonSchema,
            stream.name, stream.namespace
        )
        return ParquetSerializedBuffer(formatConfig, schema)
    }
}