/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verifyNoMoreInteractions;

import com.amazonaws.services.s3.AmazonS3;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.InOrder;
import org.mockito.Mockito;

public class S3DestinationTest {

  private AmazonS3 s3;
  private S3DestinationConfig config;

  @BeforeEach
  public void setup() {
    s3 = mock(AmazonS3.class);
    config = new S3DestinationConfig(
        "fake-endpoint",
        "fake-bucket",
        "fake-bucketPath",
        "fake-region",
        "fake-accessKeyId",
        "fake-secretAccessKey",
        null);
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
