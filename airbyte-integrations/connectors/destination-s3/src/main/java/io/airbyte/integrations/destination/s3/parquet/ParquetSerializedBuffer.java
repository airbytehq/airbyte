/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.record_buffer.BaseSerializedBuffer;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.AvroRecordFactory;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.io.OutputStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.UUID;
import java.util.concurrent.Callable;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.commons.lang3.StringUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.s3a.Constants;
import org.apache.parquet.avro.AvroParquetWriter;
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.util.HadoopOutputFile;

public class ParquetSerializedBuffer extends BaseSerializedBuffer {

  private final Schema schema;
  private final AvroRecordFactory avroRecordFactory;
  private final S3DestinationConfig config;
  private ParquetWriter<Record> parquetWriter;

  public ParquetSerializedBuffer(final BufferStorage bufferStorage,
                                 final S3DestinationConfig config,
                                 final AirbyteStreamNameNamespacePair stream,
                                 final ConfiguredAirbyteCatalog catalog)
      throws Exception {
    super(bufferStorage);
    // disable compression stream as it is already handled by this
    withCompression(false);
    this.config = config;
    final JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
    schema = schemaConverter.getAvroSchema(catalog.getStreams()
        .stream()
        .filter(s -> s.getStream().getName().equals(stream.getName()) && StringUtils.equals(s.getStream().getNamespace(), stream.getNamespace()))
        .findFirst()
        .orElseThrow(() -> new RuntimeException(String.format("No such stream %s.%s", stream.getNamespace(), stream.getName())))
        .getStream()
        .getJsonSchema(),
        stream.getName(), stream.getNamespace());
    avroRecordFactory = new AvroRecordFactory(schema, AvroConstants.JSON_CONVERTER);
  }

  @Override
  protected void createWriter(final OutputStream outputStream) throws IOException, URISyntaxException {
    final Configuration hadoopConfig = getHadoopConfig(config);
    final S3ParquetFormatConfig formatConfig = (S3ParquetFormatConfig) config.getFormatConfig();
    // TODO outputPrefix?
    final URI uri = new URI(String.format("s3a://%s/%s", config.getBucketName(), getFilename()));
    final Path path = new Path(uri);
    this.parquetWriter = AvroParquetWriter.<GenericData.Record>builder(HadoopOutputFile.fromPath(path, hadoopConfig))
        .withSchema(schema)
        .withCompressionCodec(formatConfig.getCompressionCodec())
        .withRowGroupSize(formatConfig.getBlockSize())
        .withMaxPaddingSize(formatConfig.getMaxPaddingSize())
        .withPageSize(formatConfig.getPageSize())
        .withDictionaryPageSize(formatConfig.getDictionaryPageSize())
        .withDictionaryEncoding(formatConfig.isDictionaryEncoding())
        .build();
  }

  private static Configuration getHadoopConfig(final S3DestinationConfig config) {
    final Configuration hadoopConfig = new Configuration();
    hadoopConfig.set(Constants.ACCESS_KEY, config.getAccessKeyId());
    hadoopConfig.set(Constants.SECRET_KEY, config.getSecretAccessKey());
    if (config.getEndpoint().isEmpty()) {
      hadoopConfig.set(Constants.ENDPOINT, String.format("s3.%s.amazonaws.com", config.getBucketRegion()));
    } else {
      hadoopConfig.set(Constants.ENDPOINT, config.getEndpoint());
      hadoopConfig.set(Constants.PATH_STYLE_ACCESS, "true");
    }
    hadoopConfig.set(Constants.AWS_CREDENTIALS_PROVIDER,
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider");
    return hadoopConfig;
  }

  @Override
  protected void writeRecord(final AirbyteRecordMessage recordMessage) throws IOException {
    parquetWriter.write(avroRecordFactory.getAvroRecord(UUID.randomUUID(), recordMessage));
  }

  @Override
  protected void closeWriter() throws IOException {
    parquetWriter.close();
  }

  public static CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> createFunction(final S3DestinationConfig s3DestinationConfig,
                                                                                                                                          final Callable<BufferStorage> createStorageFunction) {
    return (final AirbyteStreamNameNamespacePair stream, final ConfiguredAirbyteCatalog catalog) -> new ParquetSerializedBuffer(
        createStorageFunction.call(),
        s3DestinationConfig, stream, catalog);
  }

}
