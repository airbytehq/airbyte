/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.startsWith;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ListObjectsRequest;
import io.airbyte.integrations.destination.s3.util.S3NameTransformer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentMatchers;

public class S3BaseChecksTest {

  private AmazonS3 s3Client;

  @BeforeEach
  public void setup() {
    s3Client = mock(AmazonS3.class);
    when(s3Client.doesObjectExist(anyString(), eq(""))).thenThrow(new IllegalArgumentException("Object path must not be empty"));
    when(s3Client.putObject(anyString(), eq(""), anyString())).thenThrow(new IllegalArgumentException("Object path must not be empty"));
  }

  @Test
  public void attemptWriteAndDeleteS3Object_should_createSpecificFiles() {
    S3DestinationConfig config = new S3DestinationConfig(
        null,
        "test_bucket",
        "test/bucket/path",
        null,
        null,
        null,
        null,
        s3Client);
    S3StorageOperations operations = new S3StorageOperations(new S3NameTransformer(), s3Client, config);
    when(s3Client.doesObjectExist("test_bucket", "test/bucket/path/")).thenReturn(false);

    S3BaseChecks.attemptS3WriteAndDelete(operations, config, "test/bucket/path");

    verify(s3Client).putObject(eq("test_bucket"), startsWith("test/bucket/path/_airbyte_connection_test_"), anyString());
    verify(s3Client).listObjects(ArgumentMatchers.<ListObjectsRequest>argThat(request -> "test_bucket".equals(request.getBucketName())));
    verify(s3Client).deleteObject(eq("test_bucket"), startsWith("test/bucket/path/_airbyte_connection_test_"));
  }

  @Test
  public void attemptWriteAndDeleteS3Object_should_skipDirectoryCreateIfRootPath() {
    S3DestinationConfig config = new S3DestinationConfig(
        null,
        "test_bucket",
        "",
        null,
        null,
        null,
        null,
        s3Client);
    S3StorageOperations operations = new S3StorageOperations(new S3NameTransformer(), s3Client, config);

    S3BaseChecks.attemptS3WriteAndDelete(operations, config, "");

    verify(s3Client, never()).putObject("test_bucket", "", "");
    verify(s3Client).putObject(eq("test_bucket"), startsWith("_airbyte_connection_test_"), anyString());
    verify(s3Client).listObjects(ArgumentMatchers.<ListObjectsRequest>argThat(request -> "test_bucket".equals(request.getBucketName())));
    verify(s3Client).deleteObject(eq("test_bucket"), startsWith("_airbyte_connection_test_"));
  }

  @Test
  public void attemptWriteAndDeleteS3Object_should_skipDirectoryCreateIfNullPath() {
    S3DestinationConfig config = new S3DestinationConfig(
        null,
        "test_bucket",
        null,
        null,
        null,
        null,
        null,
        s3Client);
    S3StorageOperations operations = new S3StorageOperations(new S3NameTransformer(), s3Client, config);

    S3BaseChecks.attemptS3WriteAndDelete(operations, config, null);

    verify(s3Client, never()).putObject("test_bucket", "", "");
    verify(s3Client).putObject(eq("test_bucket"), startsWith("_airbyte_connection_test_"), anyString());
    verify(s3Client).listObjects(ArgumentMatchers.<ListObjectsRequest>argThat(request -> "test_bucket".equals(request.getBucketName())));
    verify(s3Client).deleteObject(eq("test_bucket"), startsWith("_airbyte_connection_test_"));
  }

}
