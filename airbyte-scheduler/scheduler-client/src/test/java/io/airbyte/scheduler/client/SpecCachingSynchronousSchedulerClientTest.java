/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
