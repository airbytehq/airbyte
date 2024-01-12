/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

public class RedshiftFileBufferTest {

  private final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of("secrets/config_staging.json")));
  private final RedshiftStagingS3Destination destination = new RedshiftStagingS3Destination();

  @Test
  public void testGetFileBufferDefault() {
    assertEquals(destination.getNumberOfFileBuffers(config), FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  @Test
  public void testGetFileBufferMaxLimited() {
    ((ObjectNode) config).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 100);
    assertEquals(destination.getNumberOfFileBuffers(config), FileBuffer.MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  @Test
  public void testGetMinimumFileBufferCount() {
    ((ObjectNode) config).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 1);
    // User cannot set number of file counts below the default file buffer count, which is existing
    // behavior
    assertEquals(destination.getNumberOfFileBuffers(config), FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

}
