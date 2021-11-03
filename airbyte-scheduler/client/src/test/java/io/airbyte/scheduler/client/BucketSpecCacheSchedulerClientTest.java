/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.Optional;
import java.util.function.Function;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

class BucketSpecCacheSchedulerClientTest {

  private SynchronousSchedulerClient defaultClientMock;
  private Function<String, Optional<ConnectorSpecification>> bucketSpecFetcherMock;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() {
    defaultClientMock = mock(SynchronousSchedulerClient.class);
    bucketSpecFetcherMock = mock(Function.class);
  }

  @Test
  void testGetsSpecIfPresent() throws IOException {
    when(bucketSpecFetcherMock.apply("source-pokeapi:0.1.0")).thenReturn(Optional.of(new ConnectorSpecification()));
    final BucketSpecCacheSchedulerClient client = new BucketSpecCacheSchedulerClient(defaultClientMock, bucketSpecFetcherMock);
    assertEquals(new ConnectorSpecification(), client.createGetSpecJob("source-pokeapi:0.1.0").getOutput());
    verifyNoInteractions(defaultClientMock);
  }

  @Test
  void testCallsDelegateIfNotPresent() throws IOException {
    when(bucketSpecFetcherMock.apply("source-pokeapi:0.1.0")).thenReturn(Optional.empty());
    when(defaultClientMock.createGetSpecJob("source-pokeapi:0.1.0"))
        .thenReturn(new SynchronousResponse<>(new ConnectorSpecification(), mock(SynchronousJobMetadata.class)));
    final BucketSpecCacheSchedulerClient client = new BucketSpecCacheSchedulerClient(defaultClientMock, bucketSpecFetcherMock);
    assertEquals(new ConnectorSpecification(), client.createGetSpecJob("source-pokeapi:0.1.0").getOutput());
  }

  @Test
  void testCallsDelegateIfException() throws IOException {
    when(bucketSpecFetcherMock.apply("source-pokeapi:0.1.0")).thenThrow(new RuntimeException("induced exception"));
    when(defaultClientMock.createGetSpecJob("source-pokeapi:0.1.0"))
        .thenReturn(new SynchronousResponse<>(new ConnectorSpecification(), mock(SynchronousJobMetadata.class)));
    final BucketSpecCacheSchedulerClient client = new BucketSpecCacheSchedulerClient(defaultClientMock, bucketSpecFetcherMock);
    assertEquals(new ConnectorSpecification(), client.createGetSpecJob("source-pokeapi:0.1.0").getOutput());
  }

  // todo (cgardens) - this is essentially an integration test. run it manually to sanity check that
  // the client can pull. from the spec cache bucket. when we have a better setup for integation
  // testing for the platform we should move it there.
  @Disabled
  @Test
  void testGetsSpecFromBucket() throws IOException {
    when(bucketSpecFetcherMock.apply("source-pokeapi:0.1.0")).thenReturn(Optional.of(new ConnectorSpecification()));
    // todo (cgardens) - replace with prod bucket.
    final BucketSpecCacheSchedulerClient client = new BucketSpecCacheSchedulerClient(defaultClientMock, "cg-specs");
    final ConnectorSpecification actualSpec = client.createGetSpecJob("source-pokeapi:0.1.0").getOutput();
    assertTrue(actualSpec.getDocumentationUrl().toString().contains("poke"));
  }

}
