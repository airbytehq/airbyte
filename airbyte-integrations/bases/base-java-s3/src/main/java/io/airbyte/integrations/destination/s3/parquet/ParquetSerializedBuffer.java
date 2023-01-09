/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.AvroRecordFactory;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData.Record;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.parquet.avro.AvroParquetWriter;
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.util.HadoopOutputFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The {@link io.airbyte.integrations.destination.record_buffer.BaseSerializedBuffer} class
 * abstracts the {@link io.airbyte.integrations.destination.record_buffer.BufferStorage} from the
 * details of the format the data is going to be stored in.
 *
 * Unfortunately, the Parquet library doesn't allow us to manipulate the output stream and forces us
 * to go through {@link HadoopOutputFile} instead. So we can't benefit from the abstraction
 * described above. Therefore, we re-implement the necessary methods to be used as
 * {@link SerializableBuffer}, while data will be buffered in such a hadoop file.
 */
public class ParquetSerializedBuffer implements SerializableBuffer {

  private static final Logger LOGGER = LoggerFactory.getLogger(ParquetSerializedBuffer.class);

  private final AvroRecordFactory avroRecordFactory;
  private final ParquetWriter<Record> parquetWriter;
  private final Path bufferFile;
  private InputStream inputStream;
  private Long lastByteCount;
  private boolean isClosed;

  public ParquetSerializedBuffer(final S3DestinationConfig config,
                                 final AirbyteStreamNameNamespacePair stream,
                                 final ConfiguredAirbyteCatalog catalog)
      throws IOException {
    final JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
    final Schema schema = schemaConverter.getAvroSchema(catalog.getStreams()
        .stream()
        .filter(s -> s.getStream().getName().equals(stream.getName()) && StringUtils.equals(s.getStream().getNamespace(), stream.getNamespace()))
        .findFirst()
        .orElseThrow(() -> new RuntimeException(String.format("No such stream %s.%s", stream.getNamespace(), stream.getName())))
        .getStream()
        .getJsonSchema(),
        stream.getName(), stream.getNamespace());
    bufferFile = Files.createTempFile(UUID.randomUUID().toString(), ".parquet");
    Files.deleteIfExists(bufferFile);
    avroRecordFactory = new AvroRecordFactory(schema, AvroConstants.JSON_CONVERTER);
    final S3ParquetFormatConfig formatConfig = (S3ParquetFormatConfig) config.getFormatConfig();
    parquetWriter = AvroParquetWriter.<Record>builder(HadoopOutputFile
        .fromPath(new org.apache.hadoop.fs.Path(bufferFile.toUri()), new Configuration()))
        .withSchema(schema)
        .withCompressionCodec(formatConfig.getCompressionCodec())
        .withRowGroupSize(formatConfig.getBlockSize())
        .withMaxPaddingSize(formatConfig.getMaxPaddingSize())
        .withPageSize(formatConfig.getPageSize())
        .withDictionaryPageSize(formatConfig.getDictionaryPageSize())
        .withDictionaryEncoding(formatConfig.isDictionaryEncoding())
        .build();
    inputStream = null;
    isClosed = false;
    lastByteCount = 0L;
  }

  @Override
  public long accept(final AirbyteRecordMessage recordMessage) throws Exception {
    if (inputStream == null && !isClosed) {
      final long startCount = getByteCount();
      parquetWriter.write(avroRecordFactory.getAvroRecord(UUID.randomUUID(), recordMessage));
      return getByteCount() - startCount;
    } else {
      throw new IllegalCallerException("Buffer is already closed, it cannot accept more messages");
    }
  }

  @Override
  public void flush() throws Exception {
    if (inputStream == null && !isClosed) {
      getByteCount();
      parquetWriter.close();
      inputStream = new FileInputStream(bufferFile.toFile());
      LOGGER.info("Finished writing data to {} ({})", getFilename(), FileUtils.byteCountToDisplaySize(getByteCount()));
    }
  }

  @Override
  public long getByteCount() {
    if (inputStream != null) {
      // once the parquetWriter is closed, we can't query how many bytes are in it, so we cache the last
      // count
      return lastByteCount;
    }
    lastByteCount = parquetWriter.getDataSize();
    return lastByteCount;
  }

  @Override
  public String getFilename() throws IOException {
    return bufferFile.getFileName().toString();
  }

  @Override
  public File getFile() throws IOException {
    return bufferFile.toFile();
  }

  @Override
  public InputStream getInputStream() {
    return inputStream;
  }

  @Override
  public long getMaxTotalBufferSizeInBytes() {
    return FileBuffer.MAX_TOTAL_BUFFER_SIZE_BYTES;
  }

  @Override
  public long getMaxPerStreamBufferSizeInBytes() {
    return FileBuffer.MAX_PER_STREAM_BUFFER_SIZE_BYTES;
  }

  @Override
  public int getMaxConcurrentStreamsInBuffer() {
    return FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER;
  }

  @Override
  public void close() throws Exception {
    if (!isClosed) {
      inputStream.close();
      Files.deleteIfExists(bufferFile);
      isClosed = true;
    }
  }

  public static CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> createFunction(final S3DestinationConfig s3DestinationConfig) {
    return (final AirbyteStreamNameNamespacePair stream, final ConfiguredAirbyteCatalog catalog) -> new ParquetSerializedBuffer(s3DestinationConfig,
        stream, catalog);
  }

}
