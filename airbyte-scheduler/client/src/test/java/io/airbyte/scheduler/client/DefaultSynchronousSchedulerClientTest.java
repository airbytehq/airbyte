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
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.workers.temporal.JobMetadata;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalResponse;
import java.io.IOException;
import java.nio.file.Path;
import java.util.UUID;
import java.util.function.Function;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

// the goal here is to test the "execute" part of this class and all of the various exceptional
// cases. then separately test submission of each job type without having to re-test all of the
// execution exception cases again.
class DefaultSynchronousSchedulerClientTest {

  private static final Path LOG_PATH = Path.of("/tmp");
  private static final String DOCKER_IMAGE = "foo/bar";
  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID UUID1 = UUID.randomUUID();
  private static final UUID UUID2 = UUID.randomUUID();
  private static final JsonNode CONFIGURATION = Jsons.jsonNode(ImmutableMap.builder()
      .put("username", "airbyte")
      .put("password", "abc")
      .build());
  private static final SourceConnection SOURCE_CONNECTION = new SourceConnection()
      .withSourceId(UUID1)
      .withSourceDefinitionId(UUID2)
      .withConfiguration(CONFIGURATION);
  private static final DestinationConnection DESTINATION_CONNECTION = new DestinationConnection()
      .withDestinationId(UUID1)
      .withDestinationDefinitionId(UUID2)
      .withConfiguration(CONFIGURATION);

  private TemporalClient temporalClient;
  private JobTracker jobTracker;
  private DefaultSynchronousSchedulerClient schedulerClient;

  @BeforeEach
  void setup() {
    temporalClient = mock(TemporalClient.class);
    jobTracker = mock(JobTracker.class);
    schedulerClient = new DefaultSynchronousSchedulerClient(temporalClient, jobTracker);
  }

  private static JobMetadata createMetadata(boolean succeeded) {
    return new JobMetadata(
        succeeded,
        LOG_PATH);
  }

  @Nested
  @DisplayName("Test execute method.")
  class ExecuteSynchronousJob {

    @SuppressWarnings("unchecked")
    @Test
    void testExecuteJobSuccess() {
      final UUID sourceDefinitionId = UUID.randomUUID();
      final Function<UUID, TemporalResponse<String>> function = mock(Function.class);
      when(function.apply(any(UUID.class))).thenReturn(new TemporalResponse<>("hello", createMetadata(true)));

      final SynchronousResponse<String> response = schedulerClient
          .execute(ConfigType.DISCOVER_SCHEMA, sourceDefinitionId, function, WORKSPACE_ID);

      assertNotNull(response);
      assertEquals("hello", response.getOutput());
      assertEquals(ConfigType.DISCOVER_SCHEMA, response.getMetadata().getConfigType());
      assertTrue(response.getMetadata().getConfigId().isPresent());
      assertEquals(sourceDefinitionId, response.getMetadata().getConfigId().get());
      assertTrue(response.getMetadata().isSucceeded());
      assertEquals(LOG_PATH, response.getMetadata().getLogPath());

      verify(jobTracker).trackDiscover(any(UUID.class), eq(sourceDefinitionId), eq(WORKSPACE_ID), eq(JobState.STARTED));
      verify(jobTracker).trackDiscover(any(UUID.class), eq(sourceDefinitionId), eq(WORKSPACE_ID), eq(JobState.SUCCEEDED));
    }

    @SuppressWarnings("unchecked")
    @Test
    void testExecuteJobFailure() {
      final UUID sourceDefinitionId = UUID.randomUUID();
      final Function<UUID, TemporalResponse<String>> function = mock(Function.class);
      when(function.apply(any(UUID.class))).thenReturn(new TemporalResponse<>(null, createMetadata(false)));

      final SynchronousResponse<String> response = schedulerClient
          .execute(ConfigType.DISCOVER_SCHEMA, sourceDefinitionId, function, WORKSPACE_ID);

      assertNotNull(response);
      assertNull(response.getOutput());
      assertEquals(ConfigType.DISCOVER_SCHEMA, response.getMetadata().getConfigType());
      assertTrue(response.getMetadata().getConfigId().isPresent());
      assertEquals(sourceDefinitionId, response.getMetadata().getConfigId().get());
      assertFalse(response.getMetadata().isSucceeded());
      assertEquals(LOG_PATH, response.getMetadata().getLogPath());

      verify(jobTracker).trackDiscover(any(UUID.class), eq(sourceDefinitionId), eq(WORKSPACE_ID), eq(JobState.STARTED));
      verify(jobTracker).trackDiscover(any(UUID.class), eq(sourceDefinitionId), eq(WORKSPACE_ID), eq(JobState.FAILED));
    }

    @SuppressWarnings("unchecked")
    @Test
    void testExecuteRuntimeException() {
      final UUID sourceDefinitionId = UUID.randomUUID();
      final Function<UUID, TemporalResponse<String>> function = mock(Function.class);
      when(function.apply(any(UUID.class))).thenThrow(new RuntimeException());

      assertThrows(
          RuntimeException.class,
          () -> schedulerClient.execute(ConfigType.DISCOVER_SCHEMA, sourceDefinitionId, function, WORKSPACE_ID));

      verify(jobTracker).trackDiscover(any(UUID.class), eq(sourceDefinitionId), eq(WORKSPACE_ID), eq(JobState.STARTED));
      verify(jobTracker).trackDiscover(any(UUID.class), eq(sourceDefinitionId), eq(WORKSPACE_ID), eq(JobState.FAILED));
    }

  }

  @Nested
  @DisplayName("Test job creation for each configuration type.")
  class TestJobCreation {

    @Test
    void testCreateSourceCheckConnectionJob() {
      final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
          .withConnectionConfiguration(SOURCE_CONNECTION.getConfiguration())
          .withDockerImage(DOCKER_IMAGE);

      final StandardCheckConnectionOutput mockOutput = mock(StandardCheckConnectionOutput.class);
      when(temporalClient.submitCheckConnection(any(UUID.class), eq(0), eq(jobCheckConnectionConfig)))
          .thenReturn(new TemporalResponse<>(mockOutput, createMetadata(true)));
      final SynchronousResponse<StandardCheckConnectionOutput> response =
          schedulerClient.createSourceCheckConnectionJob(SOURCE_CONNECTION, DOCKER_IMAGE);
      assertEquals(mockOutput, response.getOutput());
    }

    @Test
    void testCreateDestinationCheckConnectionJob() {
      final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
          .withConnectionConfiguration(DESTINATION_CONNECTION.getConfiguration())
          .withDockerImage(DOCKER_IMAGE);

      final StandardCheckConnectionOutput mockOutput = mock(StandardCheckConnectionOutput.class);
      when(temporalClient.submitCheckConnection(any(UUID.class), eq(0), eq(jobCheckConnectionConfig)))
          .thenReturn(new TemporalResponse<>(mockOutput, createMetadata(true)));
      final SynchronousResponse<StandardCheckConnectionOutput> response =
          schedulerClient.createDestinationCheckConnectionJob(DESTINATION_CONNECTION, DOCKER_IMAGE);
      assertEquals(mockOutput, response.getOutput());
    }

    @Test
    void testCreateDiscoverSchemaJob() {
      final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
          .withConnectionConfiguration(SOURCE_CONNECTION.getConfiguration())
          .withDockerImage(DOCKER_IMAGE);

      final AirbyteCatalog mockOutput = mock(AirbyteCatalog.class);
      when(temporalClient.submitDiscoverSchema(any(UUID.class), eq(0), eq(jobDiscoverCatalogConfig)))
          .thenReturn(new TemporalResponse<>(mockOutput, createMetadata(true)));
      final SynchronousResponse<AirbyteCatalog> response = schedulerClient.createDiscoverSchemaJob(SOURCE_CONNECTION, DOCKER_IMAGE);
      assertEquals(mockOutput, response.getOutput());
    }

    @Test
    void testCreateGetSpecJob() throws IOException {
      final JobGetSpecConfig jobSpecConfig = new JobGetSpecConfig().withDockerImage(DOCKER_IMAGE);

      final ConnectorSpecification mockOutput = mock(ConnectorSpecification.class);
      when(temporalClient.submitGetSpec(any(UUID.class), eq(0), eq(jobSpecConfig)))
          .thenReturn(new TemporalResponse<>(mockOutput, createMetadata(true)));
      final SynchronousResponse<ConnectorSpecification> response = schedulerClient.createGetSpecJob(DOCKER_IMAGE);
      assertEquals(mockOutput, response.getOutput());
    }

  }

}
