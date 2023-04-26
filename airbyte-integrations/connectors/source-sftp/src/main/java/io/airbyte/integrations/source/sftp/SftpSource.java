/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SftpSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(SftpSource.class);

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new SftpSource()).run(args);
  }

  /**
   * Check SFTP connection status and existence of working directory if set with the provided Json
   * configuration.
   *
   * @param config - json configuration for connecting SFTP
   * @return AirbyteConnectionStatus status of the connection result.
   * @throws Exception - any exception.
   */
  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    final SftpClient client = new SftpClient(config);
    try {
      final SftpCommand command = new SftpCommand(client, config);
      client.connect();
      String workingDirectory = config.has("folder_path") ? config.get("folder_path").asText() : "";
      if (StringUtils.isNotBlank(workingDirectory)) {
        command.tryChangeWorkingDirectory(workingDirectory);
      }
      client.disconnect();
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Exception attempting to connect to the server: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the server with provided configuration. \n" + e.getMessage());
    } finally {
      client.disconnect();
    }
  }

  /**
   * Discover the current schema in the SFTP server in the provided folder. For each discovered file
   * it will return stream with file name and parsed Schema
   *
   * @param config - json configuration for connecting SFTP
   * @return Description of the schema.
   * @throws Exception - any exception.
   */
  @Override
  public AirbyteCatalog discover(JsonNode config) {
    final SftpClient client = new SftpClient(config);
    try {
      final SftpCommand command = new SftpCommand(client, config);
      client.connect();
      String workingDirectory = config.has("folder_path") ? config.get("folder_path").asText() : "";
      if (StringUtils.isNotBlank(workingDirectory)) {
        command.tryChangeWorkingDirectory(workingDirectory);
      }
      Map<String, JsonNode> fileSchemas = command.getFilesSchemas();
      List<AirbyteStream> streams = fileSchemas.keySet()
          .stream()
          .map(fileName -> new AirbyteStream()
              .withName(fileName)
              .withJsonSchema(fileSchemas.get(fileName))
              .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
          .toList();
      return new AirbyteCatalog().withStreams(streams);
    } catch (Exception e) {
      LOGGER.error("Exception attempting to discover the server: ", e);
      throw new RuntimeException(e);
    } finally {
      client.disconnect();
    }
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) {
    final SftpClient client = new SftpClient(config);
    final SftpCommand command = new SftpCommand(client, config);
    client.connect();
    String workingDirectory = config.has("folder_path") ? config.get("folder_path").asText() : "";
    if (StringUtils.isNotBlank(workingDirectory)) {
      command.tryChangeWorkingDirectory(workingDirectory);
    }

    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();

    catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .forEach(stream -> {
          AutoCloseableIterator<JsonNode> fileData = getFileDataIterator(command, stream);
          AutoCloseableIterator<AirbyteMessage> messageIterator = getMessageIterator(fileData, stream.getName());
          iteratorList.add(messageIterator);
        });
    return AutoCloseableIterators
        .appendOnClose(AutoCloseableIterators.concatWithEagerClose(iteratorList, AirbyteTraceMessageUtility::emitStreamStatusTrace), () -> {
          LOGGER.info("Closing server connection.");
          client.disconnect();
          LOGGER.info("Closed server connection.");
        });
  }

  private AutoCloseableIterator<AirbyteMessage> getMessageIterator(final AutoCloseableIterator<JsonNode> recordIterator,
                                                                   final String streamName) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(r)));
  }

  private AutoCloseableIterator<JsonNode> getFileDataIterator(final SftpCommand command,
                                                              final AirbyteStream stream) {
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        List<JsonNode> fileData = command.getFileData(stream.getName());
        return AutoCloseableIterators.fromIterator(fileData.iterator());
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

}
