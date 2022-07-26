/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.integrations.destination.redshift.RedshiftDestination.DestinationType;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("RedshiftDestination")
public class RedshiftDestinationTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @Test
  @DisplayName("When not given S3 credentials should use INSERT")
  public void useStandardInsert() {
    final var standardInsertConfigStub = mapper.createObjectNode();
    standardInsertConfigStub.put("method", "Standard");
    final var uploadingMethodStub = mapper.createObjectNode();
    uploadingMethodStub.set("uploading_method", standardInsertConfigStub);
    assertEquals(DestinationType.STANDARD, RedshiftDestination.determineUploadMode(uploadingMethodStub));
  }

  @Test
  @DisplayName("When given standard backward compatibility test")
  public void useStandardInsertBackwardCompatibility() {
    final var standardInsertConfigStub = mapper.createObjectNode();
    assertEquals(DestinationType.STANDARD, RedshiftDestination.determineUploadMode(standardInsertConfigStub));
  }

  @Test
  @DisplayName("When given S3 credentials should use COPY")
  public void useS3Staging() {
    final var s3StagingStub = mapper.createObjectNode();
    final var uploadingMethodStub = mapper.createObjectNode();
    s3StagingStub.put("s3_bucket_name", "fake-bucket");
    s3StagingStub.put("s3_bucket_region", "fake-region");
    s3StagingStub.put("access_key_id", "test");
    s3StagingStub.put("secret_access_key", "test key");
    s3StagingStub.put("method", "S3 Staging");
    uploadingMethodStub.set("uploading_method", s3StagingStub);
    assertEquals(DestinationType.COPY_S3, RedshiftDestination.determineUploadMode(uploadingMethodStub));
  }

  @Test
  @DisplayName("When given S3 backward compatibility test")
  public void useS3StagingBackwardCompatibility() {
    final var s3StagingStub = mapper.createObjectNode();
    s3StagingStub.put("s3_bucket_name", "fake-bucket");
    s3StagingStub.put("s3_bucket_region", "fake-region");
    s3StagingStub.put("access_key_id", "test");
    s3StagingStub.put("secret_access_key", "test key");
    assertEquals(DestinationType.COPY_S3, RedshiftDestination.determineUploadMode(s3StagingStub));
  }

}
