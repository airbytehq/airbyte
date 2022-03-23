/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import com.amazonaws.util.IOUtils;
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
import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import java.util.concurrent.Callable;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.commons.lang3.StringUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.parquet.avro.AvroParquetWriter;
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.util.HadoopOutputFile;

/**
 * This class handles some AVRO to PARQUET conversion in an intermediate temporary file.
 *
 * When the writer receives a {@link ParquetSerializedBuffer#flushWriter()} call, the data is
 * transferred from the temporary file to the OutputStream that was provided when calling
 * {@link ParquetSerializedBuffer#createWriter(OutputStream)}. (Note that this OutputStream could
 * also be coming from a {@link io.airbyte.integrations.destination.record_buffer.FileBuffer} (an
 * implementation of {@link BufferStorage}). So it would effectively use two temporary files to
 * buffer data (unless we could convert the FileBuffer into a {@link HadoopOutputFile}).
 *
 * Closing this writer will delete the temporary parquet file.
 */
public class ParquetSerializedBuffer extends BaseSerializedBuffer {

  private final Schema schema;
  private final AvroRecordFactory avroRecordFactory;
  private final S3DestinationConfig config;
  private String tempFile;
  private ParquetWriter<Record> parquetWriter;
  private OutputStream outputStream;

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
  protected void createWriter(final OutputStream outputStream) throws IOException {
    final S3ParquetFormatConfig formatConfig = (S3ParquetFormatConfig) config.getFormatConfig();
    this.outputStream = outputStream;
    tempFile = UUID.randomUUID() + ".parquet";
    parquetWriter = AvroParquetWriter.<GenericData.Record>builder(HadoopOutputFile
        .fromPath(new org.apache.hadoop.fs.Path(tempFile), new Configuration()))
        .withSchema(schema)
        .withCompressionCodec(formatConfig.getCompressionCodec())
        .withRowGroupSize(formatConfig.getBlockSize())
        .withMaxPaddingSize(formatConfig.getMaxPaddingSize())
        .withPageSize(formatConfig.getPageSize())
        .withDictionaryPageSize(formatConfig.getDictionaryPageSize())
        .withDictionaryEncoding(formatConfig.isDictionaryEncoding())
        .build();
  }

  @Override
  protected void writeRecord(final AirbyteRecordMessage recordMessage) throws IOException {
    parquetWriter.write(avroRecordFactory.getAvroRecord(UUID.randomUUID(), recordMessage));
  }

  @Override
  protected void flushWriter() throws IOException {
    parquetWriter.close();
    try (final FileInputStream tempStream = new FileInputStream(tempFile)) {
      IOUtils.copy(tempStream, outputStream);
      outputStream.flush();
    }
  }

  @Override
  protected void closeWriter() throws IOException {
    parquetWriter.close();
    Files.deleteIfExists(Path.of(tempFile));
  }

  public static CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> createFunction(final S3DestinationConfig s3DestinationConfig,
                                                                                                                                          final Callable<BufferStorage> createStorageFunction) {
    return (final AirbyteStreamNameNamespacePair stream, final ConfiguredAirbyteCatalog catalog) -> new ParquetSerializedBuffer(
        createStorageFunction.call(),
        s3DestinationConfig, stream, catalog);
  }

}
