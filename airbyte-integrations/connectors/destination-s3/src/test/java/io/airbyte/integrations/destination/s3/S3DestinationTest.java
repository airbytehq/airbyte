/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.when;

import com.amazonaws.services.s3.model.AmazonS3Exception;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.InitiateMultipartUploadRequest;
import com.amazonaws.services.s3.model.InitiateMultipartUploadResult;
import com.amazonaws.services.s3.model.ListObjectsRequest;
import com.amazonaws.services.s3.model.UploadPartRequest;
import com.amazonaws.services.s3.model.UploadPartResult;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.InOrder;
import org.mockito.Mockito;

public class S3DestinationTest {

  private AmazonS3 s3;
  private AmazonS3 s3NoAccess;
  private S3DestinationConfig config;

  @BeforeEach
  public void setup() {
    // S3 client mock for successful operations
    s3 = mock(AmazonS3.class);
    final InitiateMultipartUploadResult uploadResult = mock(InitiateMultipartUploadResult.class);
    final UploadPartResult uploadPartResult = mock(UploadPartResult.class);
    when(s3.uploadPart(any(UploadPartRequest.class))).thenReturn(uploadPartResult);
    when(s3.initiateMultipartUpload(any(InitiateMultipartUploadRequest.class))).thenReturn(uploadResult);

    // S3 client mock that throws Access Denied exception for listObjects operation
    s3NoAccess = mock(AmazonS3.class);
    doThrow(new AmazonS3Exception("Access Denied")).when(s3NoAccess).listObjects(any(ListObjectsRequest.class));
    config = new S3DestinationConfig(
        "fake-endpoint",
        "fake-bucket",
        "fake-bucketPath",
        "fake-region",
        "fake-accessKeyId",
        "fake-secretAccessKey",
        S3DestinationConfig.DEFAULT_PART_SIZE_MB, null, s3);
  }

  @Test
  public void checksS3NoListObjectPermission() {
    final S3Destination destinationFail = new S3Destination(new S3DestinationConfigFactory () {
      public S3DestinationConfig getS3DestinationConfig(final JsonNode config) {
        return new S3DestinationConfig(
            "fake-endpoint",
            "fake-bucket",
            "fake-bucketPath",
            "fake-region",
            "fake-accessKeyId",
            "fake-secretAccessKey",
            S3DestinationConfig.DEFAULT_PART_SIZE_MB,
            null, s3NoAccess);
      }
    });
    AirbyteConnectionStatus status = destinationFail.check(null);
    assertEquals(Status.FAILED, status.getStatus(), "Connection check should have failed");
    assertTrue(status.getMessage().indexOf("Access Denied") > 0, "Connection check returned wrong failure message");

    // Test that check succeeds when IAM user has listObjects permission
    final S3Destination destinationSuccess = new S3Destination(new S3DestinationConfigFactory () {
      public S3DestinationConfig getS3DestinationConfig(final JsonNode config) {
        return new S3DestinationConfig(
            "fake-endpoint",
            "fake-bucket",
            "fake-bucketPath",
            "fake-region",
            "fake-accessKeyId",
            "fake-secretAccessKey",
            S3DestinationConfig.DEFAULT_PART_SIZE_MB,
            null, s3);
      }
    });
    status = destinationSuccess.check(null);
    assertEquals(Status.SUCCEEDED, status.getStatus(), "Connection check should have succeeded");
  }

  @Test
  public void createsThenDeletesTestFile() {
    S3Destination.attemptS3WriteAndDelete(config, "fake-fileToWriteAndDelete", s3);

    // We want to enforce that putObject happens before deleteObject, so use inOrder.verify()
    final InOrder inOrder = Mockito.inOrder(s3);

    final ArgumentCaptor<String> testFileCaptor = ArgumentCaptor.forClass(String.class);
    inOrder.verify(s3).putObject(eq("fake-bucket"), testFileCaptor.capture(), anyString());

    final String testFile = testFileCaptor.getValue();
    assertTrue(testFile.startsWith("fake-fileToWriteAndDelete/_airbyte_connection_test_"), "testFile was actually " + testFile);

    inOrder.verify(s3).deleteObject("fake-bucket", testFile);

    verifyNoMoreInteractions(s3);
  }

}
