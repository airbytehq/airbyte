/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_ACCESS_KEY_ID;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_PATH;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_SECRET_ACCESS_KEY;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.CATALOG_SCHEMA;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.STAGING_OBJECT_STORE;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyDestinationConfig.get;
import static java.util.Locale.ENGLISH;
import static org.apache.commons.lang3.RandomStringUtils.randomAlphanumeric;
import static org.slf4j.LoggerFactory.getLogger;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import java.nio.file.Path;
import java.util.List;
import org.slf4j.Logger;

public class StarburstGalaxyS3DestinationAcceptanceTest
    extends StarburstGalaxyDestinationAcceptanceTest {

  private static final Logger LOGGER = getLogger(StarburstGalaxyS3DestinationAcceptanceTest.class);
  private static final String SECRETS_CONFIG_JSON = "secrets/config.json";

  @Override
  protected JsonNode getFailCheckConfig() {
    JsonNode failCheckJson = Jsons.clone(configJson);
    // set invalid credential
    ((ObjectNode) failCheckJson.get(STAGING_OBJECT_STORE))
        .put(S_3_ACCESS_KEY_ID, "fake-key")
        .put(S_3_SECRET_ACCESS_KEY, "fake-secret");
    return failCheckJson;
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    JsonNode baseConfigJson = Jsons.deserialize(IOs.readFile(Path.of(SECRETS_CONFIG_JSON)));

    // Set a random s3 bucket path and database schema for each integration test
    String randomString = randomAlphanumeric(5);
    JsonNode configJson = Jsons.clone(baseConfigJson);
    ((ObjectNode) configJson).put(CATALOG_SCHEMA, configJson.get(CATALOG_SCHEMA).asText() + "_" + randomString);
    JsonNode stagingStore = configJson.get(STAGING_OBJECT_STORE);
    ((ObjectNode) stagingStore).put(S_3_BUCKET_PATH, "test_" + randomString);

    this.configJson = configJson;
    this.galaxyDestinationConfig = get(configJson);
    S3DestinationConfig s3Config = galaxyDestinationConfig.storageConfig().getS3DestinationConfigOrThrow();
    LOGGER.info("Test full path: s3://{}/{}", s3Config.getBucketName(), s3Config.getBucketPath());

    super.setup(testEnv); // Create a database
  }

  @Override
  protected List<String> resolveIdentifier(String identifier) {
    return List.of(identifier.toLowerCase(ENGLISH));
  }

}
