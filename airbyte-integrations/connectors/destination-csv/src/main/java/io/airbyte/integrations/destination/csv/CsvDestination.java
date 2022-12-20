/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.csv;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.CommitOnStateAirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CsvDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(CsvDestination.class);

  static final String DESTINATION_PATH_FIELD = "destination_path";

  static final String DELIMITER_TYPE = "delimiter_type";

  private final StandardNameTransformer namingResolver;

  public CsvDestination() {
    namingResolver = new StandardNameTransformer();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      FileUtils.forceMkdir(getDestinationPath(config).toFile());
    } catch (final Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  /**
   * @param config - csv destination config.
   * @param catalog - schema of the incoming messages.
   * @return - a consumer to handle writing records to the filesystem.
   * @throws IOException - exception throw in manipulating the filesystem.
   */
  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws IOException {
    final Path destinationDir = getDestinationPath(config);
    final Character delimiter = getDelimiter(config);
    CSVFormat csvFormat;

    FileUtils.forceMkdir(destinationDir.toFile());

    final Map<String, WriteConfig> writeConfigs = new HashMap<>();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String tableName = namingResolver.getRawTableName(streamName);
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      final Path tmpPath = destinationDir.resolve(tmpTableName + ".csv");
      final Path finalPath = destinationDir.resolve(tableName + ".csv");
      csvFormat = CSVFormat.DEFAULT.withDelimiter(delimiter);
      csvFormat = csvFormat.withHeader(JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            JavaBaseConstants.COLUMN_NAME_DATA);
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
      if (syncMode == null) {
        throw new IllegalStateException("Undefined destination sync mode");
      }
      final boolean isAppendMode = syncMode != DestinationSyncMode.OVERWRITE;
      if (isAppendMode && finalPath.toFile().exists()) {
        Files.copy(finalPath, tmpPath, StandardCopyOption.REPLACE_EXISTING);
        csvFormat = csvFormat.withSkipHeaderRecord();
      }
      final FileWriter fileWriter = new FileWriter(tmpPath.toFile(), Charset.defaultCharset(), isAppendMode);
      final CSVPrinter printer = new CSVPrinter(fileWriter, csvFormat);
      writeConfigs.put(stream.getStream().getName(), new WriteConfig(printer, tmpPath, finalPath, delimiter));
    }

    return new CsvConsumer(writeConfigs, catalog, outputRecordCollector);
  }

  /**
   * Extract provided relative path from csv config object and append to local mount path.
   *
   * @param config - csv config object
   * @return absolute path with the relative path appended to the local volume mount.
   */
  protected Path getDestinationPath(final JsonNode config) {
    Path destinationPath = Paths.get(config.get(DESTINATION_PATH_FIELD).asText());
    Preconditions.checkNotNull(destinationPath);

    if (!destinationPath.startsWith("/local"))
      destinationPath = Path.of("/local", destinationPath.toString());
    final Path normalizePath = destinationPath.normalize();
    if (!normalizePath.startsWith("/local")) {
      throw new IllegalArgumentException("Destination file should be inside the /local directory");
    }

    return destinationPath;
  }

  /**
   * Extract provided delimiter from csv config object.
   *
   * @param config - csv config object
   * @return delimiter.
   */
  protected Character getDelimiter(final JsonNode config) {

      JsonNode tempConfig = config;
      Character delimiter;

      if (tempConfig.has(DELIMITER_TYPE)) {
        String delimiter_as_text = tempConfig.get(DELIMITER_TYPE).get("delimiter").asText();
        delimiter = (char) Integer.parseInt(delimiter_as_text.substring(2),16);
        return delimiter;
      } else {
        delimiter = ',';
      }
      Preconditions.checkNotNull(delimiter);
      return delimiter;
  }

  /**
   * This consumer writes individual records to temporary files. If all of the messages are written
   * successfully, it moves the tmp files to files named by their respective stream. If there are any
   * failures, nothing is written.
   */
  private static class CsvConsumer extends CommitOnStateAirbyteMessageConsumer {

    private final Map<String, WriteConfig> writeConfigs;
    private final ConfiguredAirbyteCatalog catalog;

    public CsvConsumer(final Map<String, WriteConfig> writeConfigs,
                       final ConfiguredAirbyteCatalog catalog,
                       final Consumer<AirbyteMessage> outputRecordCollector) {
      super(outputRecordCollector);
      this.catalog = catalog;
      LOGGER.info("initializing consumer.");

      this.writeConfigs = writeConfigs;
    }

    @Override
    protected void startTracked() {
      // todo (cgardens) - move contents of #write into this method.
    }

    @Override
    protected void acceptTracked(final AirbyteMessage message) throws Exception {
      if (message.getType() != Type.RECORD) {
        return;
      }
      final AirbyteRecordMessage recordMessage = message.getRecord();

      // ignore other message types.
      if (!writeConfigs.containsKey(recordMessage.getStream())) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
      }

      writeConfigs.get(recordMessage.getStream()).getWriter().printRecord(
          UUID.randomUUID(),
          recordMessage.getEmittedAt(),
          Jsons.serialize(recordMessage.getData()));
    }

    @Override
    public void commit() throws Exception {
      for (final WriteConfig writeConfig : writeConfigs.values()) {
        writeConfig.getWriter().flush();
      }
    }

    @Override
    protected void close(boolean hasFailed) throws IOException {
      LOGGER.info("finalizing consumer.");

      for (final Map.Entry<String, WriteConfig> entries : writeConfigs.entrySet()) {
        try {
          entries.getValue().getWriter().flush();
          entries.getValue().getWriter().close();
        } catch (final Exception e) {
          hasFailed = true;
          LOGGER.error("failed to close writer for: {}.", entries.getKey());
        }
      }
      // do not persist the data, if there are any failures.
      try {
        if (!hasFailed) {
          for (final WriteConfig writeConfig : writeConfigs.values()) {
            Files.move(writeConfig.getTmpPath(), writeConfig.getFinalPath(), StandardCopyOption.REPLACE_EXISTING);
            LOGGER.info(String.format("File output: %s", writeConfig.getFinalPath()));
          }
        } else {
          final String message = "Failed to output files in destination";
          LOGGER.error(message);
          throw new IOException(message);
        }
      } finally {
        // clean up tmp files.
        for (final WriteConfig writeConfig : writeConfigs.values()) {
          Files.deleteIfExists(writeConfig.getTmpPath());
        }
      }
    }

  }

  private static class WriteConfig {

    private final CSVPrinter writer;
    private final Path tmpPath;
    private final Path finalPath;
    private final Character delimiter;

    public WriteConfig(final CSVPrinter writer, final Path tmpPath, final Path finalPath, final Character delimiter) {
      this.writer = writer;
      this.tmpPath = tmpPath;
      this.finalPath = finalPath;
      this.delimiter = delimiter;
    }

    public CSVPrinter getWriter() {
      return writer;
    }

    public Path getTmpPath() {
      return tmpPath;
    }

    public Path getFinalPath() {
      return finalPath;
    }

    public Character getDelimiter() {
      return delimiter;
    }

  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new CsvDestination()).run(args);
  }

}
