/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DockerComposeDocumentStoreClientTest {

  private static final String KEY = "a";
  private static final String DOCUMENT = "hello";
  private static final String DOCUMENT2 = "bye";

  private DockerComposeDocumentStoreClient client;

  @BeforeEach
  void setup() throws IOException {
    final Path testRoot = Files.createTempDirectory(Path.of("/tmp"), "document_store");
    client = new DockerComposeDocumentStoreClient(testRoot);
  }

  // todo (cgardens) - possible to dedupe this test with S3CloudDocumentStoreClientTest
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
