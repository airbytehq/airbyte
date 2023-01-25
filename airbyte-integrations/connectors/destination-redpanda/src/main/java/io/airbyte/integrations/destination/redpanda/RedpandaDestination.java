/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedpandaDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedpandaDestination.class);

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new RedpandaDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    String topicName = "namespace.stream";
    RedpandaOperations redpandaOperations = null;
    try {
      RedpandaConfig redpandaConfig = RedpandaConfig.createConfig(config);
      redpandaOperations = new RedpandaOperations(redpandaConfig);
      redpandaOperations.createTopic(
          List.of(new RedpandaOperations.TopicInfo(topicName, Optional.empty(), Optional.empty())));
      redpandaOperations.putRecordBlocking(topicName, UUID.randomUUID().toString(), Jsons.emptyObject());
      redpandaOperations.flush();
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Error while trying to connect to Redpanda: ", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED);
    } finally {
      if (redpandaOperations != null) {
        try {
          redpandaOperations.deleteTopic(List.of(topicName));
        } catch (Exception e) {
          LOGGER.error("Error while deleting Redpanda topic: ", e);
        }
        redpandaOperations.close();
      }
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    RedpandaConfig redpandaConfig = RedpandaConfig.createConfig(config);
    return new RedpandaMessageConsumer(configuredCatalog, new RedpandaOperations(redpandaConfig), redpandaConfig,
        outputRecordCollector);
  }

}
