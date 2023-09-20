/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_service_bus;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.security.NoSuchAlgorithmException;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;

@SuppressWarnings("UnnecessaryUnicodeEscape")
@Slf4j
public class AzureServiceBusDestination extends BaseConnector implements Destination {

  static final String STREAM = "_stream";
  static final String NAMESPACE = "_namespace";
  static final String KEYS = "_stream_keys";

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new AzureServiceBusDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode jsonNodeConfig) {
    try {
      // check config has required values by constructing config
      AzureServiceBusConfig.fromJsonNode(jsonNodeConfig);
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      log.info("Check failed.", e);
      return new AirbyteConnectionStatus().withStatus(Status.FAILED)
          .withMessage(e.getMessage() != null ? e.getMessage() : e.toString());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
      ConfiguredAirbyteCatalog configuredCatalog,
      Consumer<AirbyteMessage> outputRecordCollector) {
    var sbConfig = AzureServiceBusConfig.fromJsonNode(config);
    try {
      return new AzureServiceBusPublisher(sbConfig, configuredCatalog, outputRecordCollector);
    } catch (NoSuchAlgorithmException e) {
      throw new RuntimeException(e);
    }
  }

}
