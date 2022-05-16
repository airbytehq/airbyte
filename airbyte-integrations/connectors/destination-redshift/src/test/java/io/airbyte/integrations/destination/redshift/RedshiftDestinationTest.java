/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.integrations.destination.redshift.RedshiftDestination.DestinationType;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("RedshiftDestination")
public class RedshiftDestinationTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @Test
  @DisplayName("When given S3 credentials should use COPY with SUPER Datatype")
  public void useCopyStrategyTestWithSuperTmpTable() {
    final var stubConfig = mapper.createObjectNode();
    stubConfig.put("s3_bucket_name", "fake-bucket");
    stubConfig.put("s3_bucket_region", "fake-region");
    stubConfig.put("access_key_id", "test");
    stubConfig.put("secret_access_key", "test key");

    assertEquals(DestinationType.COPY_S3_WITH_SUPER_TMP_TYPE, RedshiftDestination.determineUploadMode(stubConfig));
  }

  @Test
  @DisplayName("When not given S3 credentials should use INSERT with SUPER Datatype")
  public void useInsertStrategyTestWithSuperDatatype() {
    final var stubConfig = mapper.createObjectNode();
    assertEquals(DestinationType.INSERT_WITH_SUPER_TMP_TYPE, RedshiftDestination.determineUploadMode(stubConfig));
  }

}
