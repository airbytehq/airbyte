/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test.logging;

import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggingConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggingConsumer.class);

  private final TestingLoggerFactory loggerFactory;
  private final ConfiguredAirbyteCatalog configuredCatalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, TestingLogger> loggers;

  public LoggingConsumer(final TestingLoggerFactory loggerFactory,
                         final ConfiguredAirbyteCatalog configuredCatalog,
                         final Consumer<AirbyteMessage> outputRecordCollector) {
    this.loggerFactory = loggerFactory;
    this.configuredCatalog = configuredCatalog;
    this.outputRecordCollector = outputRecordCollector;
    this.loggers = new HashMap<>();
  }

  @Override
  public void start() {
    for (final ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {
      final AirbyteStream stream = configuredStream.getStream();
      final AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair.fromAirbyteStream(stream);
      final TestingLogger logger = loggerFactory.create(streamNamePair);
      loggers.put(streamNamePair, logger);
    }
  }

  @Override
  public void accept(final AirbyteMessage message) {
    if (message.getType() == Type.STATE) {
      LOGGER.info("Emitting state: {}", message);
      outputRecordCollector.accept(message);
    } else if (message.getType() == Type.TRACE) {
      LOGGER.info("Received a trace: {}", message);
    } else if (message.getType() == Type.RECORD) {
      final AirbyteRecordMessage recordMessage = message.getRecord();
      final AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);

      if (!loggers.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format(
                "Message contained record from a stream that was not in the catalog.\n  Catalog: %s\n  Message: %s",
                Jsons.serialize(configuredCatalog), Jsons.serialize(recordMessage)));
      }

      loggers.get(pair).log(recordMessage);
    }
  }

  @Override
  public void close() {}

}
