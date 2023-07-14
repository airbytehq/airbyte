/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.commons.jackson.MoreMappers.initMapper;
import static io.airbyte.commons.resources.MoreResources.readResource;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_NAME;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.STAGING_OBJECT_STORE;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyDestinationResolver.getStagingStorageType;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyDestinationResolver.isS3StagingStore;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyStagingStorageType.S3;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class StarburstGalaxyDestinationResolverTest {

  private static final ObjectMapper OBJECT_MAPPER = initMapper();

  @Test
  @DisplayName("When given staging credentials should use S3")
  public void useS3Test() {
    final ObjectNode stubLoadingMethod = OBJECT_MAPPER.createObjectNode();
    stubLoadingMethod.put(S_3_BUCKET_NAME, "fake-bucket");
    final ObjectNode stubConfig = OBJECT_MAPPER.createObjectNode();
    stubConfig.set(STAGING_OBJECT_STORE, stubLoadingMethod);
    assertTrue(isS3StagingStore(stubConfig));
  }

  @Test
  @DisplayName("Staging staging storage credentials required")
  public void stagingStorageCredentialsRequiredTest() {
    final ObjectNode stubLoadingMethod = OBJECT_MAPPER.createObjectNode();
    final ObjectNode stubConfig = OBJECT_MAPPER.createObjectNode();
    stubConfig.set(STAGING_OBJECT_STORE, stubLoadingMethod);
    assertThrows(IllegalArgumentException.class, () -> getStagingStorageType(stubConfig));
  }

  @Test
  public void testS3ConfigType() throws Exception {
    final String configFileName = "config.json";
    final JsonNode config = Jsons.deserialize(readResource(configFileName), JsonNode.class);
    final StarburstGalaxyStagingStorageType stagingStorageType = getStagingStorageType(config);
    assertEquals(S3, stagingStorageType);
  }

}
