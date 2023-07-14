/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_NAME;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.STAGING_OBJECT_STORE;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyStagingStorageType.S3;

import com.fasterxml.jackson.databind.JsonNode;

public class StarburstGalaxyDestinationResolver {

  public static StarburstGalaxyStagingStorageType getStagingStorageType(final JsonNode config) {
    if (isS3StagingStore(config)) {
      return S3;
    }
    throw new IllegalArgumentException("Staging storage configurations must be provided");
  }

  public static boolean isS3StagingStore(final JsonNode config) {
    return config.has(STAGING_OBJECT_STORE) && config.get(STAGING_OBJECT_STORE).isObject() && config.get(STAGING_OBJECT_STORE).has(S_3_BUCKET_NAME);
  }

}
