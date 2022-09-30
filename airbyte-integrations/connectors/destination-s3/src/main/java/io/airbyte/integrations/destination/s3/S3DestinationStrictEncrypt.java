/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;

public class S3DestinationStrictEncrypt extends S3Destination {

  public S3DestinationStrictEncrypt(final S3DestinationConfigFactory configFactory) {
    super(configFactory);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final S3DestinationConfig destinationConfig = this.configFactory.getS3DestinationConfig(config, super.storageProvider());

    if (!S3BaseChecks.testCustomEndpointSecured(destinationConfig.getEndpoint())) {
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Custom endpoint does not use HTTPS");
    }
    return super.check(config);
  }
}
