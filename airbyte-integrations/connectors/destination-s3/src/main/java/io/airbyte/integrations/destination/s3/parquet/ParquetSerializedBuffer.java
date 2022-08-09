/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import static io.airbyte.integrations.destination.s3.util.JavaProcessRunner.runProcess;

import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.AvroRecordFactory;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.parquet.avro.AvroParquetWriter;
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;
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
    if (formatConfig.getCompressionCodec().equals(CompressionCodecName.LZO)) {
      installNativeLzoLibraries();
    }
    parquetWriter = AvroParquetWriter.<GenericData.Record>builder(HadoopOutputFile
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

  private void installNativeLzoLibraries() throws IOException {
    final String osName = System.getProperty("os.name").replace(' ', '_');
    final String currentDir = System.getProperty("user.dir");
    final String architecture = resolveArchitecture();

    LOGGER.info("OS {} architecture {}: ", osName, architecture);
    Runtime runtime = Runtime.getRuntime();
    if (osName.equals("Linux")) {
      if (architecture.equals("amd64-64")) {
        try {
          runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get update");
          runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get install lzop liblzo2-2 liblzo2-dev -y");
        } catch (InterruptedException e) {
          LOGGER.error("Failed to install native-lzo library for " + architecture);
        }
      }
      // libgplcompression.so is out-of-the-box for amd64-64 but must be compiled manually for other
      // processors architecture
      else {
        try {
          runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get update");
          runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get install lzop liblzo2-2 liblzo2-dev " +
              "wget curl unzip zip build-essential maven git -y");
          runProcess(currentDir, runtime, "/bin/sh", "-c", "wget http://www.oberhumer.com/opensource/lzo/download/lzo-2.10.tar.gz -P /usr/local/tmp");
          runProcess("/usr/local/tmp/", runtime, "/bin/sh", "-c", "tar xvfz lzo-2.10.tar.gz");
          runProcess("/usr/local/tmp/lzo-2.10/", runtime, "/bin/sh", "-c", "./configure --enable-shared --prefix /usr/local/lzo-2.10");
          runProcess("/usr/local/tmp/lzo-2.10/", runtime, "/bin/sh", "-c", "make && make install");
          runProcess(currentDir, runtime, "/bin/sh", "-c", "git clone https://github.com/twitter/hadoop-lzo.git /usr/lib/hadoop/lib/hadoop-lzo/");
          runProcess(currentDir, runtime, "/bin/sh", "-c", "curl -s https://get.sdkman.io | bash");
          runProcess(currentDir, runtime, "/bin/bash", "-c", "source /root/.sdkman/bin/sdkman-init.sh;" +
              " sdk install java 8.0.342-librca;" +
              " sdk use java 8.0.342-librca;" +
              " cd /usr/lib/hadoop/lib/hadoop-lzo/ " +
              "&& C_INCLUDE_PATH=/usr/local/lzo-2.10/include " +
              "LIBRARY_PATH=/usr/local/lzo-2.10/lib mvn clean package");
          runProcess(currentDir, runtime, "/bin/sh", "-c",
              "find /usr/lib/hadoop/lib/hadoop-lzo/ -name '*libgplcompression*' -exec cp {} /usr/lib/ \\;");
        } catch (InterruptedException e) {
          LOGGER.error("Failed to install native-lzo library for " + architecture);
        }
      }
    } else {
      throw new RuntimeException(osName + "is not currently supported for LZO compression");
    }
  }

  private static String resolveArchitecture() {
    return System.getProperty("os.arch") + "-" + System.getProperty("sun.arch.data.model");
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
