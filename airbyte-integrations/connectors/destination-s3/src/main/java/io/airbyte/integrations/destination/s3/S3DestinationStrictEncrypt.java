/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import java.util.Map;

public class S3DestinationStrictEncrypt extends S3Destination {

  public S3DestinationStrictEncrypt() {
    super();
  }

  @VisibleForTesting
  protected S3DestinationStrictEncrypt(final S3DestinationConfigFactory configFactory, Map<String, String> environment) {
    super(configFactory, environment);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final S3DestinationConfig destinationConfig =
        this.getConfigFactory().getS3DestinationConfig(config, super.storageProvider(), super.getEnvironment());

    // Fails early to avoid extraneous validations checks if custom endpoint is not secure
    if (!S3BaseChecks.testCustomEndpointSecured(destinationConfig.getEndpoint())) {
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Custom endpoint does not use HTTPS");
    }
    return super.check(config);
  }

}
