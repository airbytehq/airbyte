/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.copy.s3;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import org.junit.jupiter.api.Test;

public class S3CopyConfigTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  @Test
  public void setsDefaultValues() throws IOException {
    final boolean purgeStagingData = S3CopyConfig.shouldPurgeStagingData(OBJECT_MAPPER.readTree("{}"));

    assertTrue(purgeStagingData);
  }

  @Test
  public void parsesPurgeStagingDataCorrectly() throws IOException {
    final boolean purgeStagingData = S3CopyConfig.shouldPurgeStagingData(OBJECT_MAPPER.readTree(
        """
        {
          "purge_staging_data": false
        }
        """));

    assertFalse(purgeStagingData);
  }

}
