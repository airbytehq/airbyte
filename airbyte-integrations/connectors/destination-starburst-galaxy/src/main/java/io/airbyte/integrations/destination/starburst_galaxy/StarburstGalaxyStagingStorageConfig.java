/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.OBJECT_STORE_TYPE;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyStagingStorageType.S3;
import static org.slf4j.LoggerFactory.getLogger;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import org.slf4j.Logger;

public abstract class StarburstGalaxyStagingStorageConfig {

  private static final Logger LOGGER = getLogger(StarburstGalaxyStagingStorageConfig.class);

  public static StarburstGalaxyStagingStorageConfig getStarburstGalaxyStagingStorageConfig(final JsonNode config) {
    final JsonNode typeConfig = config.get(OBJECT_STORE_TYPE);
    LOGGER.info("Galaxy staging storage type config: {}", typeConfig.toString());
    final StarburstGalaxyStagingStorageType storageType = StarburstGalaxyStagingStorageType.valueOf(typeConfig.asText().toUpperCase());
    if (storageType == S3) {
      return new StarburstGalaxyS3StagingStorageConfig(config);
    }
    throw new RuntimeException("Unsupported staging object store type: " + storageType);
  }

  public S3DestinationConfig getS3DestinationConfigOrThrow() {
    throw new UnsupportedOperationException("Cannot get S3 destination config from " + this.getClass().getSimpleName());
  }

}
