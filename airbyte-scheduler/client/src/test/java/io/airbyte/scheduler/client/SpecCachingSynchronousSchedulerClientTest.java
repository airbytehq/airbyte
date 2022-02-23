/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SpecCachingSynchronousSchedulerClientTest {

  private static final String DOCKER_IMAGE = "airbyte/space_cop";

  private SynchronousSchedulerClient decoratedClient;
  private CachingSynchronousSchedulerClient client;
  private SynchronousResponse<ConnectorSpecification> response1;
  private SynchronousResponse<ConnectorSpecification> response2;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() {
    response1 = mock(SynchronousResponse.class, RETURNS_DEEP_STUBS);
    response2 = mock(SynchronousResponse.class, RETURNS_DEEP_STUBS);
    decoratedClient = mock(SynchronousSchedulerClient.class);
    client = new SpecCachingSynchronousSchedulerClient(decoratedClient);
  }

  @Test
  void testCreateGetSpecJobCacheCacheMiss() throws IOException {
    when(decoratedClient.createGetSpecJob(DOCKER_IMAGE)).thenReturn(response1);
    when(response1.isSuccess()).thenReturn(true);
    assertEquals(response1, client.createGetSpecJob(DOCKER_IMAGE));
    verify(decoratedClient, times(1)).createGetSpecJob(DOCKER_IMAGE);
  }

  @Test
  void testCreateGetSpecJobFails() throws IOException {
    when(decoratedClient.createGetSpecJob(DOCKER_IMAGE)).thenReturn(response1).thenReturn(response2);
    when(response1.isSuccess()).thenReturn(false);
    when(response2.isSuccess()).thenReturn(true);
    client.createGetSpecJob(DOCKER_IMAGE);
    assertEquals(response2, client.createGetSpecJob(DOCKER_IMAGE));
    verify(decoratedClient, times(2)).createGetSpecJob(DOCKER_IMAGE);
  }

  @Test
  void testCreateGetSpecJobCacheCacheHit() throws IOException {
    when(decoratedClient.createGetSpecJob(DOCKER_IMAGE)).thenReturn(response1);
    when(response1.isSuccess()).thenReturn(true);
    client.createGetSpecJob(DOCKER_IMAGE);
    assertEquals(response1, client.createGetSpecJob(DOCKER_IMAGE));
    verify(decoratedClient, times(1)).createGetSpecJob(DOCKER_IMAGE);
  }

  @Test
  void testInvalidateCache() throws IOException {
    when(decoratedClient.createGetSpecJob(DOCKER_IMAGE)).thenReturn(response1).thenReturn(response2);
    when(response1.isSuccess()).thenReturn(true);
    when(response2.isSuccess()).thenReturn(true);
    client.createGetSpecJob(DOCKER_IMAGE);
    client.resetCache();
    assertEquals(response2, client.createGetSpecJob(DOCKER_IMAGE));
    verify(decoratedClient, times(2)).createGetSpecJob(DOCKER_IMAGE);
  }

}
