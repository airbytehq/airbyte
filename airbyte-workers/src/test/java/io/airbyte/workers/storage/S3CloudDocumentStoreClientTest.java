/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

@Tag("logger-client")
class S3CloudDocumentStoreClientTest {

  private static final String BUCKET_NAME = "airbyte-kube-integration-logging-test";
  private static final Region REGION = Region.of("us-west-2");
  private static final String KEY = "a";
  private static final String DOCUMENT = "hello";
  private static final String DOCUMENT2 = "bye";

  private S3CloudDocumentStoreClient s3CloudDocumentStoreClient;

  @BeforeEach
  void setup() {
    final Path root = Path.of("state-test" + UUID.randomUUID());
    final S3Client s3Client = S3Client.builder().region(REGION).build();
    s3CloudDocumentStoreClient = new S3CloudDocumentStoreClient(s3Client, BUCKET_NAME, root);
  }

  // todo (cgardens) - possible to dedupe this test with GcsCloudDocumentStoreClientTest
  @Test
  void test() {
    final Optional<String> emptyResponse = s3CloudDocumentStoreClient.read(KEY);
    assertFalse(emptyResponse.isPresent());

    s3CloudDocumentStoreClient.write(KEY, DOCUMENT);
    final Optional<String> actualDocument = s3CloudDocumentStoreClient.read(KEY);
    assertTrue(actualDocument.isPresent());
    assertEquals(DOCUMENT, actualDocument.get());

    s3CloudDocumentStoreClient.write(KEY, DOCUMENT2);
    final Optional<String> actualDocumentUpdated = s3CloudDocumentStoreClient.read(KEY);
    assertTrue(actualDocumentUpdated.isPresent());
    assertEquals(DOCUMENT2, actualDocumentUpdated.get());

    assertTrue(s3CloudDocumentStoreClient.delete(KEY));
    assertFalse(s3CloudDocumentStoreClient.delete(KEY));

    final Optional<String> emptyResponseAfterDeletion = s3CloudDocumentStoreClient.read(KEY);
    assertFalse(emptyResponseAfterDeletion.isPresent());
  }

}
