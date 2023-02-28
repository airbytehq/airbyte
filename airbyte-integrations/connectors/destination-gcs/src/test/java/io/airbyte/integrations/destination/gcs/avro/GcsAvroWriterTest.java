/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.sql.Timestamp;
import java.time.Instant;
import org.junit.jupiter.api.Test;

class GcsAvroWriterTest {

  @Test
  public void generatesCorrectObjectPath() throws IOException {
    final GcsAvroWriter writer = new GcsAvroWriter(
        new GcsDestinationConfig(
            "fake-bucket",
            "fake-bucketPath",
            "fake-bucketRegion",
            new GcsHmacKeyCredentialConfig("fake-access-id", "fake-secret"),
            new S3AvroFormatConfig(new ObjectMapper().createObjectNode())),
        mock(AmazonS3.class, RETURNS_DEEP_STUBS),
        new ConfiguredAirbyteStream()
            .withStream(new AirbyteStream()
                .withNamespace("fake-namespace")
                .withName("fake-stream").withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))),
        Timestamp.from(Instant.ofEpochMilli(1234)),
        null);

    assertEquals("fake-bucketPath/fake-namespace/fake-stream/1970_01_01_1234_0.avro", writer.getOutputPath());
  }

}
