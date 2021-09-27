/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class SnowflakeDestinationTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @Test
  @DisplayName("When given S3 credentials should use COPY")
  public void useS3CopyStrategyTest() {
    var stubLoadingMethod = mapper.createObjectNode();
    stubLoadingMethod.put("s3_bucket_name", "fake-bucket");
    stubLoadingMethod.put("access_key_id", "test");
    stubLoadingMethod.put("secret_access_key", "test key");

    var stubConfig = mapper.createObjectNode();
    stubConfig.set("loading_method", stubLoadingMethod);

    assertTrue(SnowflakeDestination.isS3Copy(stubConfig));
  }

  @Test
  @DisplayName("When given GCS credentials should use COPY")
  public void useGcsCopyStrategyTest() {
    var stubLoadingMethod = mapper.createObjectNode();
    stubLoadingMethod.put("project_id", "my-project");
    stubLoadingMethod.put("bucket_name", "my-bucket");
    stubLoadingMethod.put("credentials_json", "hunter2");

    var stubConfig = mapper.createObjectNode();
    stubConfig.set("loading_method", stubLoadingMethod);

    assertTrue(SnowflakeDestination.isGcsCopy(stubConfig));
  }

  @Test
  @DisplayName("When not given S3 credentials should use INSERT")
  public void useInsertStrategyTest() {
    var stubLoadingMethod = mapper.createObjectNode();
    var stubConfig = mapper.createObjectNode();
    stubConfig.set("loading_method", stubLoadingMethod);
    assertFalse(SnowflakeDestination.isS3Copy(stubConfig));
  }

}
