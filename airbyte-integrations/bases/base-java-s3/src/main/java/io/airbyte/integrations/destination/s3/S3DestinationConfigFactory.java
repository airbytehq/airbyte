/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import javax.annotation.Nonnull;

public class S3DestinationConfigFactory {

  public S3DestinationConfig getS3DestinationConfig(final JsonNode config, @Nonnull final StorageProvider storageProvider) {
    return S3DestinationConfig.getS3DestinationConfig(config, storageProvider);
  }

}
