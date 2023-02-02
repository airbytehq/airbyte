/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.createGcsConfig;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getCommonCatalog;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getSchemaTooDeepNestedDepth;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.runDestinationWrite;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;
import org.junit.jupiter.api.Test;

class BigQueryDenormalizedGcsDestinationTest extends BigQueryDenormalizedDestinationTest {

  @Override
  protected JsonNode createConfig() throws IOException {
    return createGcsConfig();
  }

  @Test
  void testTooDeepNestedDepth() {
    try {
      runDestinationWrite(getCommonCatalog(getSchemaTooDeepNestedDepth(), datasetId), config, MESSAGE_USERS12);
    } catch (Exception e) {
      assert (e.getCause().getMessage().contains("nested too deeply"));
    }
  }

}
