/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("RedshiftDestination")
public class RedshiftDestinationTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @Test
  @DisplayName("When given S3 credentials should use COPY")
  public void useCopyStrategyTest() {
    var stubConfig = mapper.createObjectNode();
    stubConfig.put("s3_bucket_name", "fake-bucket");
    stubConfig.put("s3_bucket_region", "fake-region");
    stubConfig.put("access_key_id", "test");
    stubConfig.put("secret_access_key", "test key");

    assertTrue(RedshiftDestination.isCopy(stubConfig));
  }

  @Test
  @DisplayName("When not given S3 credentials should use INSERT")
  public void useInsertStrategyTest() {
    var stubConfig = mapper.createObjectNode();
    assertFalse(RedshiftDestination.isCopy(stubConfig));
  }

}
