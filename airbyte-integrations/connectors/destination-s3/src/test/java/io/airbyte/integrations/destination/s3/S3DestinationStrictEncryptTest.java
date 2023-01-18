/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.InitiateMultipartUploadRequest;
import com.amazonaws.services.s3.model.InitiateMultipartUploadResult;
import com.amazonaws.services.s3.model.UploadPartRequest;
import com.amazonaws.services.s3.model.UploadPartResult;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class S3DestinationStrictEncryptTest {

  private AmazonS3 s3;
  private S3DestinationConfigFactory factoryConfig;

  @BeforeEach
  public void setup() {
    s3 = mock(AmazonS3.class);
    final InitiateMultipartUploadResult uploadResult = mock(InitiateMultipartUploadResult.class);
    final UploadPartResult uploadPartResult = mock(UploadPartResult.class);
    when(s3.uploadPart(any(UploadPartRequest.class))).thenReturn(uploadPartResult);
    when(s3.initiateMultipartUpload(any(InitiateMultipartUploadRequest.class))).thenReturn(uploadResult);

    factoryConfig = new S3DestinationConfigFactory() {

      public S3DestinationConfig getS3DestinationConfig(final JsonNode config, final StorageProvider storageProvider) {
        return S3DestinationConfig.create("fake-bucket", "fake-bucketPath", "fake-region")
            .withEndpoint("https://s3.example.com")
            .withAccessKeyCredential("fake-accessKeyId", "fake-secretAccessKey")
            .withS3Client(s3)
            .get();
      }

    };
  }

  /**
   * Test that checks if user is using a connection that is HTTPS only
   */
  @Test
  public void checksCustomEndpointIsHttpsOnly() {
    final S3Destination destinationWithHttpsOnlyEndpoint = new S3DestinationStrictEncrypt(factoryConfig);
    final AirbyteConnectionStatus status = destinationWithHttpsOnlyEndpoint.check(null);
    assertEquals(Status.SUCCEEDED, status.getStatus(), "custom endpoint did not contain `s3-accesspoint`");
  }

  /**
   * Test that checks if user is using a connection that is deemed insecure since it does not always
   * enforce HTTPS only
   * <p>
   * https://docs.aws.amazon.com/general/latest/gr/s3.html
   * </p>
   */
  @Test
  public void checksCustomEndpointIsNotHttpsOnly() {
    final S3Destination destinationWithStandardUnsecuredEndpoint = new S3DestinationStrictEncrypt(new S3DestinationConfigFactory() {

      public S3DestinationConfig getS3DestinationConfig(final JsonNode config, final StorageProvider storageProvider) {
        return S3DestinationConfig.create("fake-bucket", "fake-bucketPath", "fake-region")
            .withEndpoint("s3.us-west-1.amazonaws.com")
            .withAccessKeyCredential("fake-accessKeyId", "fake-secretAccessKey")
            .withS3Client(s3)
            .get();
      }

    });
    final AirbyteConnectionStatus status = destinationWithStandardUnsecuredEndpoint.check(null);
    assertEquals(Status.FAILED, status.getStatus());
  }

}
