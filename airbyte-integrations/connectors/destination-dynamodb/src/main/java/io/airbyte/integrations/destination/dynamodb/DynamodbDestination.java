/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import com.amazonaws.Protocol;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DynamodbDestination extends BaseConnector implements Destination {

  private static final String NON_SECURE_URL_ERR_MSG = "Server Endpoint requires HTTPS";
  private static final Logger LOGGER = LoggerFactory.getLogger(DynamodbDestination.class);

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new DynamodbDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final DynamodbDestinationConfig dynamodbDestinationConfig =
          DynamodbDestinationConfig.getDynamodbDestinationConfig(config);

      // enforce ssl connection
      if (isNotSsl(dynamodbDestinationConfig.getEndpoint())) {
        return new AirbyteConnectionStatus()
            .withStatus(AirbyteConnectionStatus.Status.FAILED)
            .withMessage(NON_SECURE_URL_ERR_MSG);
      }

      DynamodbChecker.attemptDynamodbWriteAndDelete(dynamodbDestinationConfig);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the DynamoDB table: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the DynamoDB table with the provided configuration. \n" + e
              .getMessage());
    }
  }

  private boolean isNotSsl(String endpoint) throws MalformedURLException {
    return !endpoint.isBlank() &&
        new URL(endpoint).getProtocol().equals(Protocol.HTTP.toString());
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog configuredCatalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    // TODO
    return new DynamodbConsumer(DynamodbDestinationConfig.getDynamodbDestinationConfig(config), configuredCatalog, outputRecordCollector);
  }

}
