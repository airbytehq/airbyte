/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.cloud.storage.Blob;
import com.google.cloud.storage.Storage;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class GcsBucketSpecFetcherTest {

  private static final String BUCKET_NAME = "bucket";
  private static final String DOCKER_REPOSITORY = "image";
  private static final String DOCKER_IMAGE_TAG = "0.1.0";
  private static final String DOCKER_IMAGE = DOCKER_REPOSITORY + ":" + DOCKER_IMAGE_TAG;
  private static final String SPEC_PATH = Path.of("specs").resolve(DOCKER_REPOSITORY).resolve(DOCKER_IMAGE_TAG).resolve("spec.json").toString();

  private Storage storage;
  private Blob specBlob;
  private final ConnectorSpecification spec = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo", "bar")));

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws IOException {
    storage = mock(Storage.class);

    final byte[] specBytes = Jsons.toBytes(Jsons.jsonNode(spec));
    specBlob = mock(Blob.class);
    when(specBlob.getContent()).thenReturn(specBytes);
  }

  @Test
  void testGetsSpecIfPresent() throws IOException {
    when(storage.get(BUCKET_NAME, SPEC_PATH)).thenReturn(specBlob);

    final GcsBucketSpecFetcher bucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME);
    final Optional<ConnectorSpecification> returnedSpec = bucketSpecFetcher.attemptFetch(DOCKER_IMAGE);

    assertTrue(returnedSpec.isPresent());
    assertEquals(spec, returnedSpec.get());
  }

  @Test
  void testReturnsEmptyIfNotPresent() throws IOException {
    when(storage.get(BUCKET_NAME, SPEC_PATH)).thenReturn(null);

    final GcsBucketSpecFetcher bucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME);
    final Optional<ConnectorSpecification> returnedSpec = bucketSpecFetcher.attemptFetch(DOCKER_IMAGE);

    assertTrue(returnedSpec.isEmpty());
  }

  @Test
  void testReturnsEmptyIfInvalidSpec() throws IOException {
    final Blob invalidSpecBlob = mock(Blob.class);
    when(invalidSpecBlob.getContent()).thenReturn("{\"notASpec\": true}".getBytes(StandardCharsets.UTF_8));
    when(storage.get(BUCKET_NAME, SPEC_PATH)).thenReturn(invalidSpecBlob);

    final GcsBucketSpecFetcher bucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME);
    final Optional<ConnectorSpecification> returnedSpec = bucketSpecFetcher.attemptFetch(DOCKER_IMAGE);

    assertTrue(returnedSpec.isEmpty());
  }

}
