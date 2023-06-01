/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

import com.fasterxml.jackson.core.io.JsonStringEncoder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.CommitOnStateAirbyteMessageConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SelectdbConsumer extends CommitOnStateAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(SelectdbConsumer.class);

  private final ConfiguredAirbyteCatalog catalog;
  private final Map<String, SelectdbWriteConfig> writeConfigs;

  private JsonStringEncoder jsonEncoder;

  public SelectdbConsumer(
                          final Map<String, SelectdbWriteConfig> writeConfigs,
                          final ConfiguredAirbyteCatalog catalog,
                          final Consumer<AirbyteMessage> outputRecordCollector) {
    super(outputRecordCollector);
    jsonEncoder = JsonStringEncoder.getInstance();
    this.catalog = catalog;
    this.writeConfigs = writeConfigs;
    LOGGER.info("initializing SelectdbConsumer.");
  }

  @Override
  public void commit() throws Exception {
    for (final SelectdbWriteConfig writeConfig : writeConfigs.values()) {
      writeConfig.getWriter().flush();
    }
  }

  @Override
  protected void startTracked() throws Exception {}

  @Override
  protected void acceptTracked(AirbyteMessage msg) throws Exception {
    if (msg.getType() != AirbyteMessage.Type.RECORD) {
      return;
    }
    final AirbyteRecordMessage recordMessage = msg.getRecord();
    if (!writeConfigs.containsKey(recordMessage.getStream())) {
      throw new IllegalArgumentException(
          String.format(
              "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
              Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
    }

    writeConfigs.get(recordMessage.getStream()).getWriter().printRecord(
        UUID.randomUUID(),
        // new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS").format(new Date(recordMessage.getEmittedAt())),
        recordMessage.getEmittedAt(),
        new String(jsonEncoder.quoteAsString(Jsons.serialize(recordMessage.getData()))));

  }

  @Override
  protected void close(boolean hasFailed) throws Exception {
    LOGGER.info("finalizing SelectdbConsumer");
    for (final Map.Entry<String, SelectdbWriteConfig> entries : writeConfigs.entrySet()) {
      try {
        entries.getValue().getWriter().flush();
        entries.getValue().getWriter().close();
      } catch (final Exception e) {
        hasFailed = true;
        LOGGER.error("failed to close writer for: {}", entries.getKey());
      }
    }

    try {
      for (final SelectdbWriteConfig value : writeConfigs.values()) {
        value.getsci().firstCommit();
      }
    } catch (final Exception e) {
      hasFailed = true;
      final String message = "Failed to upload selectdb stage in destination: ";
      LOGGER.error(message + e.getMessage());
    }
    try {
      if (!hasFailed) {
        for (final SelectdbWriteConfig writeConfig : writeConfigs.values()) {
          if (writeConfig.getsci().isUpload()) {
            writeConfig.getsci().commitTransaction();
          }
          LOGGER.info("upload commit (temp file:  {} ) successed ", writeConfig.getsci().getPath());
        }
      } else {
        final String message = "Failed to copy into selectdb in destination";
        LOGGER.error(message);
        throw new IOException(message);
      }
    } finally {
      for (final SelectdbWriteConfig writeConfig : writeConfigs.values()) {
        Files.deleteIfExists(writeConfig.getsci().getPath());
        writeConfig.getsci().close();
      }
    }

  }

}
