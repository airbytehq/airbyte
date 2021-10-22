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
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import java.io.IOException;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SpecFetcherTest {

  private static final String DOCKER_REPOSITORY = "foo";
  private static final String DOCKER_IMAGE_TAG = "bar";
  private static final String IMAGE_NAME = DOCKER_REPOSITORY + ":" + DOCKER_IMAGE_TAG;

  private SynchronousSchedulerClient schedulerJobClient;
  private SynchronousResponse<ConnectorSpecification> response;
  private ConnectorSpecification connectorSpecification;
  private StandardSourceDefinition sourceDefinition;
  private StandardDestinationDefinition destinationDefinition;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() {
    schedulerJobClient = mock(SynchronousSchedulerClient.class);
    response = mock(SynchronousResponse.class);
    connectorSpecification = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo", "bar")));
    sourceDefinition = new StandardSourceDefinition().withDockerRepository(DOCKER_REPOSITORY).withDockerImageTag(DOCKER_IMAGE_TAG);
    destinationDefinition = new StandardDestinationDefinition().withDockerRepository(DOCKER_REPOSITORY).withDockerImageTag(DOCKER_IMAGE_TAG);
  }

  @Test
  void testGetSpecFromDockerImageSuccess() throws IOException {
    when(schedulerJobClient.createGetSpecJob(IMAGE_NAME)).thenReturn(response);
    when(response.isSuccess()).thenReturn(true);
    when(response.getOutput()).thenReturn(connectorSpecification);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertEquals(connectorSpecification, specFetcher.getSpec(IMAGE_NAME));
  }

  @Test
  void testGetSpecFromDockerImageFail() throws IOException {
    when(schedulerJobClient.createGetSpecJob(IMAGE_NAME)).thenReturn(response);
    when(response.isSuccess()).thenReturn(false);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertThrows(IllegalStateException.class, () -> specFetcher.getSpec(IMAGE_NAME));
  }

  @Test
  void testGetSpecFromSourceDefinitionNotNull() throws IOException {
    sourceDefinition = sourceDefinition.withSpec(connectorSpecification);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertEquals(connectorSpecification, specFetcher.getSpec(sourceDefinition));
  }

  @Test
  void testGetSpecFromSourceDefinitionNull() throws IOException {
    when(schedulerJobClient.createGetSpecJob(IMAGE_NAME)).thenReturn(response);
    when(response.isSuccess()).thenReturn(true);
    when(response.getOutput()).thenReturn(connectorSpecification);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertEquals(connectorSpecification, specFetcher.getSpec(sourceDefinition));
  }

  @Test
  void testGetSpecFromDestinationDefinitionNotNull() throws IOException {
    destinationDefinition = destinationDefinition.withSpec(connectorSpecification);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertEquals(connectorSpecification, specFetcher.getSpec(destinationDefinition));
  }

  @Test
  void testGetSpecFromDestinationDefinitionNull() throws IOException {
    when(schedulerJobClient.createGetSpecJob(IMAGE_NAME)).thenReturn(response);
    when(response.isSuccess()).thenReturn(true);
    when(response.getOutput()).thenReturn(connectorSpecification);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    assertEquals(connectorSpecification, specFetcher.getSpec(destinationDefinition));
  }

  @Test
  void testGetSpecJobResponseFromSourceReturnsMockedJobMetadata() throws IOException {
    sourceDefinition = sourceDefinition.withSpec(connectorSpecification);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    final SynchronousResponse<ConnectorSpecification> response = specFetcher.getSpecJobResponse(sourceDefinition);

    assertEquals(ConfigType.GET_SPEC, response.getMetadata().getConfigType());
    assertEquals(Optional.empty(), response.getMetadata().getConfigId());
    assertEquals(connectorSpecification, response.getOutput());
  }

  @Test
  void testGetSpecJobResponseFromDestinationReturnsMockedJobMetadata() throws IOException {
    destinationDefinition = destinationDefinition.withSpec(connectorSpecification);

    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    final SynchronousResponse<ConnectorSpecification> response = specFetcher.getSpecJobResponse(destinationDefinition);

    assertEquals(ConfigType.GET_SPEC, response.getMetadata().getConfigType());
    assertEquals(Optional.empty(), response.getMetadata().getConfigId());
    assertEquals(connectorSpecification, response.getOutput());
  }

}
