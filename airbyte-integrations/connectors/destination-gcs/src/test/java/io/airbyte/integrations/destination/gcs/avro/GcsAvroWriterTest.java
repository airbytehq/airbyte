/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
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
            null,
            new S3AvroFormatConfig(new ObjectMapper().createObjectNode())),
        mock(AmazonS3.class, RETURNS_DEEP_STUBS),
        new ConfiguredAirbyteStream()
            .withStream(new AirbyteStream()
                .withNamespace("fake-namespace")
                .withName("fake-stream")),
        Timestamp.from(Instant.ofEpochMilli(1234)),
        null);

    assertEquals("fake-bucketPath/fake_namespace/fake_stream/1970_01_01_1234_0.avro", writer.getOutputPath());
  }

}
