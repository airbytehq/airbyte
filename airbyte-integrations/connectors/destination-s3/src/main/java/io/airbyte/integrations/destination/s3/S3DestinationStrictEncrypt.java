/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;

public class S3DestinationStrictEncrypt extends S3Destination {

  public S3DestinationStrictEncrypt() {
    super();
  }

  @VisibleForTesting
  protected S3DestinationStrictEncrypt(final S3DestinationConfigFactory configFactory) {
    super(configFactory);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final S3DestinationConfig destinationConfig = this.configFactory.getS3DestinationConfig(config, super.storageProvider());

    // Fails early to avoid extraneous validations checks if custom endpoint is not secure
    if (!S3BaseChecks.testCustomEndpointSecured(destinationConfig.getEndpoint())) {
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Custom endpoint does not use HTTPS");
    }
    return super.check(config);
  }

}
