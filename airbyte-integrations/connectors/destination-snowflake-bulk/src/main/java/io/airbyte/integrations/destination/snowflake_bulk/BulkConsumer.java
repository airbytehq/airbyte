/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake_bulk;

import com.fasterxml.jackson.databind.JsonNode;
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

public class BulkConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BulkConsumer.class);

  private static final String CONFIG_STAGE_KEY = "snowflake_stage_name";
  private static final String CONFIG_FORMAT_KEY = "snowflake_file_format";

  private final JsonNode config;
  private final ConfiguredAirbyteCatalog configuredCatalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, MyLogger> loggers;

  private final String configStaging;
  private final String configFormat;

  public BulkConsumer(final JsonNode config,
      final ConfiguredAirbyteCatalog configuredCatalog,
      final Consumer<AirbyteMessage> outputRecordCollector) {
    this.config = config;
    this.configuredCatalog = configuredCatalog;
    this.outputRecordCollector = outputRecordCollector;
    this.loggers = new HashMap<>();

    this.configStaging = config.get(CONFIG_STAGE_KEY).asText();
    this.configFormat = config.get(CONFIG_FORMAT_KEY).asText();
  }

  @Override
  public void start() {
    for (final ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {
      final AirbyteStream stream = configuredStream.getStream();
      final AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair.fromAirbyteStream(stream);
      final MyLogger logger = new MyLogger(streamNamePair, 1000);
      loggers.put(streamNamePair, logger);
    }

    LOGGER.info("start staging:{} format:{}", this.configStaging, this.configFormat);
  }

  @Override
  public void accept(final AirbyteMessage message) {
    if (message.getType() == Type.STATE) {
      LOGGER.info("Emitting state: {}", message);
      outputRecordCollector.accept(message);
      return;
    } else if (message.getType() != Type.RECORD) {
      return;
    }

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

  @Override
  public void close() {
  }

}
