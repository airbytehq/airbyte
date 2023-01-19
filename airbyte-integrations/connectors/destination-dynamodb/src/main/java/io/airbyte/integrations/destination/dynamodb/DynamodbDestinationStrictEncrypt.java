/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;

public class DynamodbDestinationStrictEncrypt extends DynamodbDestination {

  protected static final String NON_SECURE_URL_ERR_MSG = "Server Endpoint requires HTTPS";

  public DynamodbDestinationStrictEncrypt() {
    super();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final DynamodbDestinationConfig dynamodbDestinationConfig =
        DynamodbDestinationConfig.getDynamodbDestinationConfig(config);

    // enforce ssl connection
    if (!DynamodbChecker.testCustomEndpointSecured(dynamodbDestinationConfig.getEndpoint())) {
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(NON_SECURE_URL_ERR_MSG);
    }

    return super.check(config);
  }

}
