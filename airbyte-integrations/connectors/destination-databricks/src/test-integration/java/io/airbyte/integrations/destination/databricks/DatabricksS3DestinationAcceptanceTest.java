/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static io.airbyte.integrations.destination.databricks.utils.DatabricksConstants.DATABRICKS_DATA_SOURCE_KEY;
import static io.airbyte.integrations.destination.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_KEY;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_ACCESS_KEY_ID;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_SECRET_ACCESS_KEY;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.DeleteObjectsResult;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.List;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabricksS3DestinationAcceptanceTest extends DatabricksDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksS3DestinationAcceptanceTest.class);
  private static final String SECRETS_CONFIG_JSON = "secrets/config.json";

  private S3DestinationConfig s3Config;
  private AmazonS3 s3Client;

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode failCheckJson = Jsons.clone(configJson);
    // set invalid credential
    ((ObjectNode) failCheckJson.get(DATABRICKS_DATA_SOURCE_KEY))
        .put(S_3_ACCESS_KEY_ID, "fake-key")
        .put(S_3_SECRET_ACCESS_KEY, "fake-secret");
    return failCheckJson;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    final JsonNode baseConfigJson = Jsons.deserialize(IOs.readFile(Path.of(SECRETS_CONFIG_JSON)));

    // Set a random s3 bucket path and database schema for each integration test
    final String randomString = RandomStringUtils.randomAlphanumeric(5);
    final JsonNode configJson = Jsons.clone(baseConfigJson);
    ((ObjectNode) configJson).put(DATABRICKS_SCHEMA_KEY, "integration_test_" + randomString);

    this.configJson = configJson;
    this.databricksConfig = DatabricksDestinationConfig.get(configJson);
    this.s3Config = databricksConfig.storageConfig().getS3DestinationConfigOrThrow();
    LOGGER.info("Test full path: s3://{}/{}", s3Config.getBucketName(), s3Config.getBucketPath());

    this.s3Client = s3Config.getS3Client();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    // clean up s3
    final List<KeyVersion> keysToDelete = new LinkedList<>();
    final List<S3ObjectSummary> objects = s3Client
        .listObjects(s3Config.getBucketName(), s3Config.getBucketPath())
        .getObjectSummaries();
    for (final S3ObjectSummary object : objects) {
      keysToDelete.add(new KeyVersion(object.getKey()));
    }

    if (keysToDelete.size() > 0) {
      LOGGER.info("Tearing down test bucket path: {}/{}", s3Config.getBucketName(),
          s3Config.getBucketPath());
      final DeleteObjectsResult result = s3Client
          .deleteObjects(new DeleteObjectsRequest(s3Config.getBucketName()).withKeys(keysToDelete));
      LOGGER.info("Deleted {} file(s).", result.getDeletedObjects().size());
    }
    s3Client.shutdown();

    super.tearDown(testEnv);
  }

}
