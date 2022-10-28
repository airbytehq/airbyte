/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import java.util.Map;
import org.junit.jupiter.api.Test;

class CompressionTypeHelperTest {

  @Test
  public void testGetCompressionType() {
    assertEquals(
        S3DestinationConstants.DEFAULT_COMPRESSION_TYPE,
        CompressionTypeHelper.parseCompressionType(null));

    assertEquals(
        CompressionType.NO_COMPRESSION,
        CompressionTypeHelper.parseCompressionType(Jsons.jsonNode(Map.of("compression_type", "No Compression"))));

    assertEquals(
        CompressionType.GZIP,
        CompressionTypeHelper.parseCompressionType(Jsons.jsonNode(Map.of("compression_type", "GZIP"))));
  }

}
