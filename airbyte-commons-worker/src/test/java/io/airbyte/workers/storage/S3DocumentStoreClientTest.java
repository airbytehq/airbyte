/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

@Tag("cloud-storage")
class S3DocumentStoreClientTest {

  private static final String BUCKET_NAME = "airbyte-kube-integration-logging-test";
  private static final Region REGION = Region.of("us-west-2");
  private static final String KEY = "a";
  private static final String DOCUMENT = "hello";
  private static final String DOCUMENT2 = "bye";

  private S3DocumentStoreClient client;

  @BeforeEach
  void setup() {
    final Path root = Path.of("state-test" + UUID.randomUUID());
    final S3Client s3Client = S3Client.builder().region(REGION).build();
    client = new S3DocumentStoreClient(s3Client, BUCKET_NAME, root);
  }

  // todo (cgardens) - possible to dedupe this test with GcsCloudDocumentStoreClientTest
  @Test
  void test() {
    final Optional<String> emptyResponse = client.read(KEY);
    assertFalse(emptyResponse.isPresent());

    client.write(KEY, DOCUMENT);
    final Optional<String> actualDocument = client.read(KEY);
    assertTrue(actualDocument.isPresent());
    assertEquals(DOCUMENT, actualDocument.get());

    client.write(KEY, DOCUMENT2);
    final Optional<String> actualDocumentUpdated = client.read(KEY);
    assertTrue(actualDocumentUpdated.isPresent());
    assertEquals(DOCUMENT2, actualDocumentUpdated.get());

    assertTrue(client.delete(KEY));
    assertFalse(client.delete(KEY));

    final Optional<String> emptyResponseAfterDeletion = client.read(KEY);
    assertFalse(emptyResponseAfterDeletion.isPresent());
  }

}
