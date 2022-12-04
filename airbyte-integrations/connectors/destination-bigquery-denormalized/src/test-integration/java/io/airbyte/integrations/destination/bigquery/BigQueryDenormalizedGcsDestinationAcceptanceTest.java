/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.createGcsConfig;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;

public class BigQueryDenormalizedGcsDestinationAcceptanceTest extends BigQueryDenormalizedDestinationAcceptanceTest {

  @Override
  protected JsonNode createConfig() throws IOException {
    return createGcsConfig();
  }

}
