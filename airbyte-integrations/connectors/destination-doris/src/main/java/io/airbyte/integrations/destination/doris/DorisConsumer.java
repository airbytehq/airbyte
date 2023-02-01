/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris;

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

public class DorisConsumer extends CommitOnStateAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(DorisConsumer.class);

  private final ConfiguredAirbyteCatalog catalog;
  private final Map<String, DorisWriteConfig> writeConfigs;

  private JsonStringEncoder jsonEncoder;

  public DorisConsumer(
                       final Map<String, DorisWriteConfig> writeConfigs,
                       final ConfiguredAirbyteCatalog catalog,
                       final Consumer<AirbyteMessage> outputRecordCollector) {
    super(outputRecordCollector);
    jsonEncoder = JsonStringEncoder.getInstance();
    this.catalog = catalog;
    this.writeConfigs = writeConfigs;
    LOGGER.info("initializing DorisConsumer.");
  }

  @Override
  public void commit() throws Exception {
    for (final DorisWriteConfig writeConfig : writeConfigs.values()) {
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
          String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
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
    LOGGER.info("finalizing DorisConsumer");
    for (final Map.Entry<String, DorisWriteConfig> entries : writeConfigs.entrySet()) {
      try {
        entries.getValue().getWriter().flush();
        entries.getValue().getWriter().close();
      } catch (final Exception e) {
        hasFailed = true;
        LOGGER.error("failed to close writer for: {}", entries.getKey());
      }
    }

    try {
      for (final DorisWriteConfig value : writeConfigs.values()) {
        value.getDorisStreamLoad().firstCommit();
      }
    } catch (final Exception e) {
      hasFailed = true;
      final String message = "Failed to pre-commit doris in destination: ";
      LOGGER.error(message + e.getMessage());
      for (final DorisWriteConfig value : writeConfigs.values()) {
        if (value.getDorisStreamLoad().getTxnID() > 0)
          value.getDorisStreamLoad().abortTransaction();
      }
    }

    //
    try {
      if (!hasFailed) {
        for (final DorisWriteConfig writeConfig : writeConfigs.values()) {
          if (writeConfig.getDorisStreamLoad().getTxnID() > 0)
            writeConfig.getDorisStreamLoad().commitTransaction();
          LOGGER.info(String.format("stream load commit (TxnID:  %s ) successed ", writeConfig.getDorisStreamLoad().getTxnID()));
        }
      } else {
        final String message = "Failed to commit doris in destination";
        LOGGER.error(message);
        for (final DorisWriteConfig writeConfig : writeConfigs.values()) {
          if (writeConfig.getDorisStreamLoad().getTxnID() > 0)
            writeConfig.getDorisStreamLoad().abortTransaction();
        }
        throw new IOException(message);
      }
    } finally {
      for (final DorisWriteConfig writeConfig : writeConfigs.values()) {
        Files.deleteIfExists(writeConfig.getDorisStreamLoad().getPath());
        writeConfig.getDorisStreamLoad().close();
      }
    }

  }

}
