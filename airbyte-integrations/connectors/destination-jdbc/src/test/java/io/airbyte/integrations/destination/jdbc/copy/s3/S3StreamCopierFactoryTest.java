/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class S3StreamCopierFactoryTest {

  @Nested
  public class ConfigTest {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    @Test
    public void setsDefaultValues() throws IOException {
      final boolean purgeStagingData = S3StreamCopierFactory.Config.shouldPurgeStagingData(OBJECT_MAPPER.readTree("{}"));

      assertTrue(purgeStagingData);
    }

    @Test
    public void parsesPurgeStagingDataCorrectly() throws IOException {
      final boolean purgeStagingData = S3StreamCopierFactory.Config.shouldPurgeStagingData(OBJECT_MAPPER.readTree(
          """
          {
            "purge_staging_data": false
          }
          """));

      assertFalse(purgeStagingData);
    }

  }

}
