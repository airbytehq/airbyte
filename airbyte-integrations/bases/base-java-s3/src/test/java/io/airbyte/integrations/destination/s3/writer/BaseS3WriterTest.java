/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.writer;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.template.S3FilenameTemplateParameterObject;
import java.io.IOException;
import java.sql.Timestamp;
import org.junit.jupiter.api.Test;

class BaseS3WriterTest {

  @Test
  public void testGetOutputFilename() throws IOException {
    final Timestamp timestamp = new Timestamp(1471461319000L);
    assertEquals(
        "2016_08_17_1471461319000_0.csv",
        BaseS3Writer.determineOutputFilename(S3FilenameTemplateParameterObject
            .builder()
            .s3Format(S3Format.CSV)
            .timestamp(timestamp)
            .build()));
  }

}
