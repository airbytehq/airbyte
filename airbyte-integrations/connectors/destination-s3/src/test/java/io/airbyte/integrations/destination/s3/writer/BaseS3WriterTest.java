/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.writer;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.destination.s3.S3Format;
import java.sql.Timestamp;
import org.junit.jupiter.api.Test;

class BaseS3WriterTest {

  @Test
  public void testGetOutputFilename() {
    Timestamp timestamp = new Timestamp(1471461319000L);
    assertEquals(
        "2016_08_17_1471461319000_0.csv",
        BaseS3Writer.getOutputFilename(timestamp, S3Format.CSV));
  }

}
