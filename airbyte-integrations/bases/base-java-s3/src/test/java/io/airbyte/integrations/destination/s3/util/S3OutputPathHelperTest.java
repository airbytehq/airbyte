/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.Lists;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class S3OutputPathHelperTest {

  @Test
  @DisplayName("getOutputPrefix")
  public void testGetOutputPrefix() {
    // No namespace
    assertEquals("bucket_path/stream_name", S3OutputPathHelper
        .getOutputPrefix("bucket_path",
            new AirbyteStream().withName("stream_name").withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))));

    // With namespace
    assertEquals("bucket_path/namespace/stream_name", S3OutputPathHelper
        .getOutputPrefix("bucket_path",
            new AirbyteStream().withNamespace("namespace").withName("stream_name")
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))));

    // With empty namespace
    assertEquals("bucket_path/stream_name", S3OutputPathHelper
        .getOutputPrefix("bucket_path",
            new AirbyteStream().withNamespace("").withName("stream_name").withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))));

    // With namespace with slash chart in the end
    assertEquals("bucket_path/namespace/stream_name", S3OutputPathHelper
        .getOutputPrefix("bucket_path",
            new AirbyteStream().withNamespace("namespace/").withName("stream_name")
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))));

    // With namespace with slash chart in the name
    assertEquals("bucket_path/namespace/subfolder/stream_name", S3OutputPathHelper
        .getOutputPrefix("bucket_path",
            new AirbyteStream().withNamespace("namespace/subfolder/").withName("stream_name")
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))));

    // With an AWS Glue crawler
    assertEquals("bucket_path/namespace/date=2022-03-15", S3OutputPathHelper
        .getOutputPrefix("bucket_path",
            new AirbyteStream().withNamespace("namespace").withName("date=2022-03-15")
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))));
  }

}
