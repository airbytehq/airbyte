/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import java.io.IOException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SpecFetcherTest {

  private static final String IMAGE_NAME = "foo:bar";

  private SynchronousSchedulerClient schedulerJobClient;
  private SynchronousResponse<ConnectorSpecification> response;
  private ConnectorSpecification connectorSpecification;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() {
    schedulerJobClient = mock(SynchronousSchedulerClient.class);
    response = mock(SynchronousResponse.class);
    connectorSpecification = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo", "bar")));
  }

  @Test
  void testFetch() throws IOException {
    when(schedulerJobClient.createGetSpecJob(IMAGE_NAME)).thenReturn(response);
    when(response.isSuccess()).thenReturn(true);
    when(response.getOutput()).thenReturn(connectorSpecification);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertEquals(connectorSpecification, specFetcher.execute(IMAGE_NAME));
  }

  @Test
  void testFetchEmpty() throws IOException {
    when(schedulerJobClient.createGetSpecJob(IMAGE_NAME)).thenReturn(response);
    when(response.isSuccess()).thenReturn(false);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertThrows(IllegalStateException.class, () -> specFetcher.execute(IMAGE_NAME));
  }

}
