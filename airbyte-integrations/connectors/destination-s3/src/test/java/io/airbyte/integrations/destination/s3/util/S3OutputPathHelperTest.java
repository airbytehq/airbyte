/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.protocol.models.AirbyteStream;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class S3OutputPathHelperTest {

  @Test
  @DisplayName("getOutputPrefix")
  public void testGetOutputPrefix() {
    // No namespace
    assertEquals("bucket_path/stream_name", S3OutputPathHelper
        .getOutputPrefix("bucket_path", new AirbyteStream().withName("stream_name")));

    // With namespace
    assertEquals("bucket_path/namespace/stream_name", S3OutputPathHelper
        .getOutputPrefix("bucket_path",
            new AirbyteStream().withNamespace("namespace").withName("stream_name")));
  }

}
