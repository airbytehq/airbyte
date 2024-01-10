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

/**
 * Integration test testing {@link RedshiftStagingS3Destination}. The default Redshift integration
 * test credentials contain S3 credentials - this automatically causes COPY to be selected.
 */
public class RedshiftS3StagingInsertDestinationAcceptanceTest extends RedshiftDestinationAcceptanceTest {

  public JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config_staging.json")));
  }

  /*
   * FileBuffer Default Tests
   */
  @Test
  public void testGetFileBufferDefault() {
    final RedshiftStagingS3Destination destination = new RedshiftStagingS3Destination();
    assertEquals(destination.getNumberOfFileBuffers(config), FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  @Test
  public void testGetFileBufferMaxLimited() {
    final JsonNode defaultConfig = Jsons.clone(config);
    ((ObjectNode) defaultConfig).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 100);
    final RedshiftStagingS3Destination destination = new RedshiftStagingS3Destination();
    assertEquals(destination.getNumberOfFileBuffers(defaultConfig), FileBuffer.MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  @Test
  public void testGetMinimumFileBufferCount() {
    final JsonNode defaultConfig = Jsons.clone(config);
    ((ObjectNode) defaultConfig).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 1);
    final RedshiftStagingS3Destination destination = new RedshiftStagingS3Destination();
    // User cannot set number of file counts below the default file buffer count, which is existing
    // behavior
    assertEquals(destination.getNumberOfFileBuffers(defaultConfig), FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

}
