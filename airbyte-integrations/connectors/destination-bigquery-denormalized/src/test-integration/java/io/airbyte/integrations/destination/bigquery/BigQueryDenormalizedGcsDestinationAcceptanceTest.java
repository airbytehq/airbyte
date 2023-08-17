/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.createGcsConfig;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import java.io.IOException;
import org.junit.jupiter.api.Test;

public class BigQueryDenormalizedGcsDestinationAcceptanceTest extends BigQueryDenormalizedDestinationAcceptanceTest {

  @Override
  protected JsonNode createConfig() throws IOException {
    return createGcsConfig();
  }

  /*
   * FileBuffer Default Tests
   */
  @Test
  public void testGetFileBufferDefault() {
    final BigQueryDenormalizedDestination destination = new BigQueryDenormalizedDestination();
    assertEquals(destination.getNumberOfFileBuffers(config),
        FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  @Test
  public void testGetFileBufferMaxLimited() {
    final JsonNode defaultConfig = Jsons.clone(config);
    ((ObjectNode) defaultConfig.get(BigQueryConsts.LOADING_METHOD)).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 100);
    final BigQueryDenormalizedDestination destination = new BigQueryDenormalizedDestination();
    assertEquals(FileBuffer.MAX_CONCURRENT_STREAM_IN_BUFFER, destination.getNumberOfFileBuffers(defaultConfig));
  }

  @Test
  public void testGetMinimumFileBufferCount() {
    final JsonNode defaultConfig = Jsons.clone(config);
    ((ObjectNode) defaultConfig.get(BigQueryConsts.LOADING_METHOD)).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 1);
    final BigQueryDenormalizedDestination destination = new BigQueryDenormalizedDestination();
    // User cannot set number of file counts below the default file buffer count, which is existing
    // behavior
    assertEquals(FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER, destination.getNumberOfFileBuffers(defaultConfig));
  }

}
