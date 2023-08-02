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
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.ACCEPT_TERMS;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.CATALOG;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.CATALOG_SCHEMA;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.OBJECT_STORE_TYPE;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.PASSWORD;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.PORT;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.SERVER_HOSTNAME;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.STAGING_OBJECT_STORE;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.USERNAME;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyDestinationConfig.DEFAULT_STARBURST_GALAXY_PORT;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyDestinationConfig.get;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

class StarburstGalaxyDestinationConfigTest {

  private static final ObjectMapper OBJECT_MAPPER = initMapper();

  @Test
  public void testConfigCreationFromJsonS3() {
    final ObjectNode dataSourceConfig = OBJECT_MAPPER.createObjectNode()
        .put(OBJECT_STORE_TYPE, "S3")
        .put(S_3_BUCKET_NAME, "bucket_name")
        .put(S_3_BUCKET_PATH, "bucket_path")
        .put(S_3_BUCKET_REGION, "bucket_region")
        .put(S_3_ACCESS_KEY_ID, "access_key_id")
        .put(S_3_SECRET_ACCESS_KEY, "secret_access_key");

    final ObjectNode starburstGalaxyConfig = OBJECT_MAPPER.createObjectNode()
        .put(SERVER_HOSTNAME, "server_hostname")
        .put(USERNAME, "username")
        .put(PASSWORD, "password")
        .put(CATALOG, "catalog")
        .put(CATALOG_SCHEMA, "catalog_schema")
        .set(STAGING_OBJECT_STORE, dataSourceConfig);

    assertThrows(IllegalArgumentException.class, () -> get(starburstGalaxyConfig));

    starburstGalaxyConfig.put(ACCEPT_TERMS, false);
    assertThrows(IllegalArgumentException.class, () -> get(starburstGalaxyConfig));

    starburstGalaxyConfig.put(ACCEPT_TERMS, true);
    final StarburstGalaxyDestinationConfig config1 = get(starburstGalaxyConfig);
    assertEquals(DEFAULT_STARBURST_GALAXY_PORT, config1.galaxyPort());
    assertEquals(CATALOG_SCHEMA, config1.galaxyCatalogSchema());

    starburstGalaxyConfig.put(PORT, DEFAULT_STARBURST_GALAXY_PORT);
    final StarburstGalaxyDestinationConfig config2 = get(starburstGalaxyConfig);
    assertEquals(DEFAULT_STARBURST_GALAXY_PORT, config2.galaxyPort());
    assertEquals(CATALOG_SCHEMA, config2.galaxyCatalogSchema());

    assertEquals(StarburstGalaxyS3StagingStorageConfig.class, config2.storageConfig().getClass());
  }

}
