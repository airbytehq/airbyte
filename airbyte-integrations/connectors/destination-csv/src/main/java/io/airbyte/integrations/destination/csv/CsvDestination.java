/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.csv;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.FailureTrackingConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CsvDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(CsvDestination.class);

  static final String COLUMN_DATA = "data"; // we output all data as a blob to a single column.
  static final String COLUMN_AB_ID = "ab_id"; // we output all data as a blob to a single column.
  static final String COLUMN_EMITTED_AT = "emitted_at"; // we output all data as a blob to a single column.
  static final String DESTINATION_PATH_FIELD = "destination_path";

  @Override
  public ConnectorSpecification spec() throws IOException {
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      FileUtils.forceMkdir(getDestinationPath(config).toFile());
    } catch (Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  /**
   * @param config - csv destination config.
   * @param catalog - schema of the incoming messages.
   * @return - a consumer to handle writing records to the filesystem.
   * @throws IOException - exception throw in manipulating the filesytem.
   */
  @Override
  public DestinationConsumer<AirbyteMessage> write(JsonNode config, AirbyteCatalog catalog) throws IOException {
    final Path destinationDir = getDestinationPath(config);

    FileUtils.forceMkdir(destinationDir.toFile());

    final long now = Instant.now().toEpochMilli();
    final Map<String, WriteConfig> writeConfigs = new HashMap<>();
    for (final AirbyteStream stream : catalog.getStreams()) {
      final Path tmpPath = destinationDir.resolve(stream.getName() + "_" + now + ".csv");
      final Path finalPath = destinationDir.resolve(stream.getName() + ".csv");
      final FileWriter fileWriter = new FileWriter(tmpPath.toFile());
      final CSVPrinter printer = new CSVPrinter(fileWriter, CSVFormat.DEFAULT.withHeader(COLUMN_AB_ID, COLUMN_EMITTED_AT, COLUMN_DATA));
      writeConfigs.put(stream.getName(), new WriteConfig(printer, tmpPath, finalPath));
    }

    return new CsvConsumer(writeConfigs, catalog);
  }

  /**
   * Extract provided relative path from csv config object and append to local mount path.
   *
   * @param config - csv config object
   * @return absolute path with the relative path appended to the local volume mount.
   */
  private Path getDestinationPath(JsonNode config) {
    final String destinationRelativePath = config.get(DESTINATION_PATH_FIELD).asText();
    Preconditions.checkNotNull(destinationRelativePath);

    return Path.of(destinationRelativePath);
  }

  /**
   * This consumer writes individual records to temporary files. If all of the messages are written
   * successfully, it moves the tmp files to files named by their respective stream. If there are any
   * failures, nothing is written.
   */
  private static class CsvConsumer extends FailureTrackingConsumer<AirbyteMessage> {

    private final Map<String, WriteConfig> writeConfigs;
    private final AirbyteCatalog catalog;

    public CsvConsumer(Map<String, WriteConfig> writeConfigs, AirbyteCatalog catalog) {
      this.catalog = catalog;
      LOGGER.info("initializing consumer.");

      this.writeConfigs = writeConfigs;
    }

    @Override
    protected void acceptTracked(AirbyteMessage message) throws Exception {

      // ignore other message types.
      if (message.getType() == AirbyteMessage.Type.RECORD) {
        if (!writeConfigs.containsKey(message.getRecord().getStream())) {
          throw new IllegalArgumentException(
              String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                  Jsons.serialize(catalog), Jsons.serialize(message)));
        }

        writeConfigs.get(message.getRecord().getStream()).getWriter().printRecord(
            UUID.randomUUID(),
            message.getRecord().getEmittedAt(),
            Jsons.serialize(message.getRecord().getData()));
      }
    }

    @Override
    protected void close(boolean hasFailed) throws IOException {
      LOGGER.info("finalizing consumer.");

      for (final Map.Entry<String, WriteConfig> entries : writeConfigs.entrySet()) {
        try {
          entries.getValue().getWriter().flush();
          entries.getValue().getWriter().close();
        } catch (Exception e) {
          hasFailed = true;
          LOGGER.error("failed to close writer for: {}.", entries.getKey());
        }
      }
      // do not persist the data, if there are any failures.
      if (!hasFailed) {
        for (final WriteConfig writeConfig : writeConfigs.values()) {
          Files.move(writeConfig.getTmpPath(), writeConfig.getFinalPath(), StandardCopyOption.REPLACE_EXISTING);
        }
      }
      // clean up tmp files.
      for (final WriteConfig writeConfig : writeConfigs.values()) {
        Files.deleteIfExists(writeConfig.getTmpPath());
      }

    }

  }

  private static class WriteConfig {

    private final CSVPrinter writer;
    private final Path tmpPath;
    private final Path finalPath;

    public WriteConfig(CSVPrinter writer, Path tmpPath, Path finalPath) {
      this.writer = writer;
      this.tmpPath = tmpPath;
      this.finalPath = finalPath;
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

  }

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new CsvDestination()).run(args);
  }

}
