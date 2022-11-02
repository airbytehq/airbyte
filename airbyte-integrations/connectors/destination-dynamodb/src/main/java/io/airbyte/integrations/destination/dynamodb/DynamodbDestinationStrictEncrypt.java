/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DynamodbDestinationStrictEncrypt extends DynamodbDestination {

  private static final String NON_SECURE_URL_ERR_MSG = "Server Endpoint requires HTTPS";
  private static final Logger LOGGER = LoggerFactory.getLogger(DynamodbDestinationStrictEncrypt.class);

  public DynamodbDestinationStrictEncrypt() {
    super();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final DynamodbDestinationConfig dynamodbDestinationConfig =
          DynamodbDestinationConfig.getDynamodbDestinationConfig(config);

      // enforce ssl connection
      if (!DynamodbChecker.testCustomEndpointSecured(dynamodbDestinationConfig.getEndpoint())) {
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

}
