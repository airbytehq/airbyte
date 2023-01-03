/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;

/**
 * S3 copy destinations need an S3DestinationConfig to configure the basic upload behavior. We also
 * want additional flags to configure behavior that only applies to the copy-to-S3 +
 * load-into-warehouse portion. Currently this is just purgeStagingData, but this may expand.
 */
public record S3CopyConfig(boolean purgeStagingData, S3DestinationConfig s3Config) {

  public static boolean shouldPurgeStagingData(final JsonNode config) {
    if (config.get("purge_staging_data") == null) {
      return true;
    } else {
      return config.get("purge_staging_data").asBoolean();
    }
  }

  public static S3CopyConfig getS3CopyConfig(final JsonNode config) {
    return new S3CopyConfig(S3CopyConfig.shouldPurgeStagingData(config),
        S3DestinationConfig.getS3DestinationConfig(config));
  }

}
