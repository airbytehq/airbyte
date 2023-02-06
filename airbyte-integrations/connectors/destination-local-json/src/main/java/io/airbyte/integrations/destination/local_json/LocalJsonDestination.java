/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.local_json;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
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
import java.io.Writer;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LocalJsonDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(LocalJsonDestination.class);

  static final String DESTINATION_PATH_FIELD = "destination_path";

  private final StandardNameTransformer namingResolver;

  public LocalJsonDestination() {
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
   * @param config - destination config.
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

    FileUtils.forceMkdir(destinationDir.toFile());

    final Map<String, WriteConfig> writeConfigs = new HashMap<>();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final Path finalPath = destinationDir.resolve(namingResolver.getRawTableName(streamName) + ".jsonl");
      final Path tmpPath = destinationDir.resolve(namingResolver.getTmpTableName(streamName) + ".jsonl");
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
      if (syncMode == null) {
        throw new IllegalStateException("Undefined destination sync mode");
      }
      final boolean isAppendMode = syncMode != DestinationSyncMode.OVERWRITE;
      if (isAppendMode && finalPath.toFile().exists()) {
        Files.copy(finalPath, tmpPath, StandardCopyOption.REPLACE_EXISTING);
      }

      final Writer writer = new FileWriter(tmpPath.toFile(), Charset.defaultCharset(), isAppendMode);
      writeConfigs.put(stream.getStream().getName(), new WriteConfig(writer, tmpPath, finalPath));
    }

    return new JsonConsumer(writeConfigs, catalog, outputRecordCollector);
  }

  /**
   * Extract provided path.
   *
   * @param config - config object
   * @return absolute path where to write files.
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
   * This consumer writes individual records to temporary files. If all of the messages are written
   * successfully, it moves the tmp files to files named by their respective stream. If there are any
   * failures, nothing is written.
   */
  private static class JsonConsumer extends CommitOnStateAirbyteMessageConsumer {

    private final Map<String, WriteConfig> writeConfigs;
    private final ConfiguredAirbyteCatalog catalog;

    public JsonConsumer(final Map<String, WriteConfig> writeConfigs,
                        final ConfiguredAirbyteCatalog catalog,
                        final Consumer<AirbyteMessage> outputRecordCollector) {
      super(outputRecordCollector);
      LOGGER.info("initializing consumer.");
      this.catalog = catalog;
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

      final Writer writer = writeConfigs.get(recordMessage.getStream()).getWriter();
      writer.write(Jsons.serialize(ImmutableMap.of(
          JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID(),
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt(),
          JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getData())));
      writer.write(System.lineSeparator());
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

    private final Writer writer;
    private final Path tmpPath;
    private final Path finalPath;

    public WriteConfig(final Writer writer, final Path tmpPath, final Path finalPath) {
      this.writer = writer;
      this.tmpPath = tmpPath;
      this.finalPath = finalPath;
    }

    public Writer getWriter() {
      return writer;
    }

    public Path getTmpPath() {
      return tmpPath;
    }

    public Path getFinalPath() {
      return finalPath;
    }

  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new LocalJsonDestination()).run(args);
  }

}
