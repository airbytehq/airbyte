/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.parquet;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.AvroRecordFactory;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.protocol.models.*;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.commons.io.FileUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.parquet.avro.AvroParquetWriter;
import org.apache.parquet.hadoop.ParquetFileWriter;
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.regex.Pattern;

import static org.apache.hadoop.fs.Path.SEPARATOR_CHAR;
import static org.apache.hadoop.fs.Path.WINDOWS;


public class ParquetDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ParquetDestination.class);
  public static final CompressionCodecName DEFAULT_COMPRESSION_CODEC = CompressionCodecName.UNCOMPRESSED;
  public static final int DEFAULT_BLOCK_SIZE_MB = 128;
  public static final int DEFAULT_MAX_PADDING_SIZE_MB = 8;
  public static final int DEFAULT_PAGE_SIZE_KB = 1024;
  public static final int DEFAULT_DICTIONARY_PAGE_SIZE_KB = 1024;
  public static final boolean DEFAULT_DICTIONARY_ENCODING = true;
  public static final String DESTINATION_PATH_FIELD = "destination_path";

  private final StandardNameTransformer namingResolver;

  public ParquetDestination() {
    namingResolver = new StandardNameTransformer();
  }
  @Override

  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      File destinationFile = new File(getDestinationPath(config).toUri().getRawPath());
      FileUtils.forceMkdir(destinationFile);
    } catch (final Exception e) {
      LOGGER.info("Forced to make directory - 1");
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws IOException {
    final Path destinationDir = getDestinationPath(config);
    LOGGER.info("Forced to make directory - 2");

    File destinationFile = new File(destinationDir.toUri().getRawPath());
    FileUtils.forceMkdir(destinationFile);

    final Map<String, WriteConfig> writeConfigs = new HashMap<>();

    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String tableName = namingResolver.getRawTableName(streamName);
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      final Path finalPath = resolve(destinationDir, new Path(tableName + ".parquet"));
      final Path tmpPath = resolve(destinationDir, new Path(tmpTableName + ".parquet"));
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
      if (syncMode == null) {
        throw new IllegalStateException("Undefined destination sync mode");
      }
      final boolean isAppendMode = syncMode != DestinationSyncMode.OVERWRITE;
      File finalPathFile = new File(finalPath.toUri().getRawPath());
      File tmpPathFile = new File(tmpPath.toUri().getRawPath());

      if (isAppendMode && finalPathFile.exists()) {
        FileUtils.copyFile(finalPathFile, tmpPathFile);
      }
      final JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
      final Schema avroSchema = schemaConverter.getAvroSchema(stream.getStream().getJsonSchema(), stream.getStream().getName(), stream.getStream().getNamespace());
      final ParquetWriter<GenericData.Record> writer = AvroParquetWriter.
              <GenericData.Record>builder(tmpPath)
              .withSchema(avroSchema)
              .withConf(new Configuration())
              .withWriteMode(ParquetFileWriter.Mode.OVERWRITE)
              .withValidation(false)
              .withRowGroupSize(this.DEFAULT_BLOCK_SIZE_MB)
              .withPageSize(this.DEFAULT_PAGE_SIZE_KB)
              .withDictionaryPageSize(this.DEFAULT_DICTIONARY_PAGE_SIZE_KB)
              .withMaxPaddingSize(this.DEFAULT_MAX_PADDING_SIZE_MB)
              .withCompressionCodec(this.DEFAULT_COMPRESSION_CODEC)
              .withDictionaryEncoding(this.DEFAULT_DICTIONARY_ENCODING)
              .build();
      AvroRecordFactory avroRecordFactory = new AvroRecordFactory(avroSchema, AvroConstants.JSON_CONVERTER);
      writeConfigs.put(stream.getStream().getName(), new WriteConfig(writer, tmpPathFile, finalPathFile, avroRecordFactory));
    }
    return new ParquetConsumer(writeConfigs, catalog, outputRecordCollector);
  }

  private static boolean has_windows_drive(String path) {
    return (WINDOWS && Pattern.compile("^/?[a-zA-Z]:").matcher(path).find());
  }

  private static int start_position_without_windows_drive(String path) {
    if (has_windows_drive(path)) {
      return path.charAt(0) ==  SEPARATOR_CHAR ? 3 : 2;
    } else {
      return 0;
    }
  }
  public static Path resolve(Path path1, Path path2) {
    String path2Str = path2.toUri().getPath();
    path2Str = path2Str.substring(start_position_without_windows_drive(path2Str));

    return new Path(path1.toUri().getScheme(),
            path1.toUri().getAuthority(),
            path1.toUri().getPath() + '/' + path2Str);
  }
  protected Path getDestinationPath(final JsonNode config) {
    Path destinationPath = new Path(config.get(DESTINATION_PATH_FIELD).asText());
    Preconditions.checkNotNull(destinationPath);

    if (!destinationPath.toUri().getRawPath().startsWith("/data"))
      destinationPath = Path.mergePaths(new Path("/data"), destinationPath);
    if (!destinationPath.toUri().getRawPath().startsWith("/data")) {
      throw new IllegalArgumentException("Destination file should be inside the /data directory");
    }

    LOGGER.info(destinationPath.toUri().getRawPath());

    return destinationPath;
  }

  record WriteConfig(ParquetWriter writer, File tmpPathFile, File finalPathFile, AvroRecordFactory avroRecordFactory) {
  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new ParquetDestination()).run(args);
  }

}
