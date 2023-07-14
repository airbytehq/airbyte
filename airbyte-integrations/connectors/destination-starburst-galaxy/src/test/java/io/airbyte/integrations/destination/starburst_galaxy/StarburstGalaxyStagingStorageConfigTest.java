/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.commons.jackson.MoreMappers.initMapper;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_ACCESS_KEY_ID;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_NAME;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_PATH;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_REGION;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_SECRET_ACCESS_KEY;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.OBJECT_STORE_TYPE;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyStagingStorageConfig.getStarburstGalaxyStagingStorageConfig;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

public class StarburstGalaxyStagingStorageConfigTest {

  @Test
  public void testRetrieveS3Config() {
    final ObjectNode dataSourceConfig = initMapper().createObjectNode()
        .put(OBJECT_STORE_TYPE, "S3")
        .put(S_3_BUCKET_NAME, "bucket_name")
        .put(S_3_BUCKET_PATH, "bucket_path")
        .put(S_3_BUCKET_REGION, "bucket_region")
        .put(S_3_ACCESS_KEY_ID, "access_key_id")
        .put(S_3_SECRET_ACCESS_KEY, "secret_access_key");

    StarburstGalaxyStagingStorageConfig storageConfig = getStarburstGalaxyStagingStorageConfig(dataSourceConfig);
    assertNotNull(storageConfig.getS3DestinationConfigOrThrow());
  }

}
