/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import static io.airbyte.config.specs.GcsBucketSpecFetcher.CLOUD_SPEC_FILE;
import static io.airbyte.config.specs.GcsBucketSpecFetcher.DEFAULT_SPEC_FILE;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.cloud.storage.Blob;
import com.google.cloud.storage.Storage;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.protocol.models.ConnectorSpecification;
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
  private static final String DEFAULT_SPEC_PATH = Path.of("specs")
      .resolve(DOCKER_REPOSITORY).resolve(DOCKER_IMAGE_TAG).resolve(DEFAULT_SPEC_FILE).toString();
  private static final String CLOUD_SPEC_PATH = Path.of("specs")
      .resolve(DOCKER_REPOSITORY).resolve(DOCKER_IMAGE_TAG).resolve(CLOUD_SPEC_FILE).toString();

  private Storage storage;
  private Blob defaultSpecBlob;
  private Blob cloudSpecBlob;
  private final ConnectorSpecification defaultSpec = new ConnectorSpecification()
      .withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo", "bar", "mode", "oss")));
  private final ConnectorSpecification cloudSpec = new ConnectorSpecification()
      .withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo", "bar", "mode", "cloud")));

  @BeforeEach
  void setup() {
    storage = mock(Storage.class);

    defaultSpecBlob = mock(Blob.class);
    when(defaultSpecBlob.getContent()).thenReturn(Jsons.toBytes(Jsons.jsonNode(defaultSpec)));
    cloudSpecBlob = mock(Blob.class);
    when(cloudSpecBlob.getContent()).thenReturn(Jsons.toBytes(Jsons.jsonNode(cloudSpec)));
  }

  @Test
  void testGetsSpecIfPresent() {
    when(storage.get(BUCKET_NAME, DEFAULT_SPEC_PATH)).thenReturn(defaultSpecBlob);

    final GcsBucketSpecFetcher bucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME);
    final Optional<ConnectorSpecification> returnedSpec = bucketSpecFetcher.attemptFetch(DOCKER_IMAGE);

    assertTrue(returnedSpec.isPresent());
    assertEquals(defaultSpec, returnedSpec.get());
  }

  @Test
  void testReturnsEmptyIfNotPresent() {
    when(storage.get(BUCKET_NAME, DEFAULT_SPEC_PATH)).thenReturn(null);

    final GcsBucketSpecFetcher bucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME);
    final Optional<ConnectorSpecification> returnedSpec = bucketSpecFetcher.attemptFetch(DOCKER_IMAGE);

    assertTrue(returnedSpec.isEmpty());
  }

  @Test
  void testReturnsEmptyIfInvalidSpec() {
    final Blob invalidSpecBlob = mock(Blob.class);
    when(invalidSpecBlob.getContent()).thenReturn("{\"notASpec\": true}".getBytes(StandardCharsets.UTF_8));
    when(storage.get(BUCKET_NAME, DEFAULT_SPEC_PATH)).thenReturn(invalidSpecBlob);

    final GcsBucketSpecFetcher bucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME);
    final Optional<ConnectorSpecification> returnedSpec = bucketSpecFetcher.attemptFetch(DOCKER_IMAGE);

    assertTrue(returnedSpec.isEmpty());
  }

  /**
   * Test {@link GcsBucketSpecFetcher#getSpecAsBlob(String, String)}.
   */
  @Test
  void testDynamicGetSpecAsBlob() {
    when(storage.get(BUCKET_NAME, DEFAULT_SPEC_PATH)).thenReturn(defaultSpecBlob);
    when(storage.get(BUCKET_NAME, CLOUD_SPEC_PATH)).thenReturn(cloudSpecBlob);

    // under deploy deployment mode, cloud spec file will be ignored even when it exists
    final GcsBucketSpecFetcher defaultBucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME);
    assertEquals(Optional.of(defaultSpecBlob),
        defaultBucketSpecFetcher.getSpecAsBlob(DOCKER_REPOSITORY, DOCKER_IMAGE_TAG));

    // under OSS deployment mode, cloud spec file will be ignored even when it exists
    final GcsBucketSpecFetcher ossBucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME, DeploymentMode.OSS);
    assertEquals(Optional.of(defaultSpecBlob),
        ossBucketSpecFetcher.getSpecAsBlob(DOCKER_REPOSITORY, DOCKER_IMAGE_TAG));

    final GcsBucketSpecFetcher cloudBucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME, DeploymentMode.CLOUD);
    assertEquals(Optional.of(cloudSpecBlob),
        cloudBucketSpecFetcher.getSpecAsBlob(DOCKER_REPOSITORY, DOCKER_IMAGE_TAG));
  }

  /**
   * Test {@link GcsBucketSpecFetcher#getSpecAsBlob(String, String, String, DeploymentMode)}.
   */
  @Test
  void testBasicGetSpecAsBlob() {
    when(storage.get(BUCKET_NAME, DEFAULT_SPEC_PATH)).thenReturn(defaultSpecBlob);
    when(storage.get(BUCKET_NAME, CLOUD_SPEC_PATH)).thenReturn(cloudSpecBlob);

    final GcsBucketSpecFetcher bucketSpecFetcher = new GcsBucketSpecFetcher(storage, BUCKET_NAME);
    assertEquals(Optional.of(defaultSpecBlob),
        bucketSpecFetcher.getSpecAsBlob(DOCKER_REPOSITORY, DOCKER_IMAGE_TAG, DEFAULT_SPEC_FILE, DeploymentMode.OSS));
    assertEquals(Optional.of(cloudSpecBlob),
        bucketSpecFetcher.getSpecAsBlob(DOCKER_REPOSITORY, DOCKER_IMAGE_TAG, CLOUD_SPEC_FILE, DeploymentMode.OSS));
  }

}
