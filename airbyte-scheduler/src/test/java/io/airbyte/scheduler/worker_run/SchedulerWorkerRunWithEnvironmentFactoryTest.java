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

package io.airbyte.scheduler.worker_run;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.State;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.worker_run.SyncWorkerRunFactories.ResetConnectionWorkerRunFactory;
import io.airbyte.scheduler.worker_run.SyncWorkerRunFactories.SyncWorkerRunFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;
import org.mockito.ArgumentCaptor;

class SchedulerWorkerRunWithEnvironmentFactoryTest {

  private static final long JOB_ID = 1L;
  private static final int ATTEMPT_ID = 2;
  private static final JsonNode CONFIG = Jsons.jsonNode(1);
  private static final JsonNode CONFIG2 = Jsons.jsonNode(2);
  private static final JsonNode STATE = Jsons.emptyObject();
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = new ConfiguredAirbyteCatalog()
      .withStreams(Lists.newArrayList(new ConfiguredAirbyteStream().withSyncMode(SyncMode.FULL_REFRESH)));
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

  private Job job;
  private SchedulerWorkerRunWithEnvironmentFactory.Creator creator;

  private SchedulerWorkerRunWithEnvironmentFactory factory;
  private Path workspaceRoot;
  private ProcessBuilderFactory pbf;

  @BeforeEach
  void setUp() throws IOException {
    job = mock(Job.class, RETURNS_DEEP_STUBS);
    when(job.getId()).thenReturn(JOB_ID);
    when(job.getAttemptsCount()).thenReturn(ATTEMPT_ID);

    creator = mock(SchedulerWorkerRunWithEnvironmentFactory.Creator.class);
    final Path rootPath = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test");
    workspaceRoot = rootPath.resolve("abc");
    pbf = mock(ProcessBuilderFactory.class);

    factory = new SchedulerWorkerRunWithEnvironmentFactory(workspaceRoot, pbf, creator);
  }

  @ParameterizedTest
  @EnumSource(value = JobConfig.ConfigType.class,
              names = {"CHECK_CONNECTION_SOURCE", "CHECK_CONNECTION_DESTINATION"})
  void testConnection(JobConfig.ConfigType value) {
    final JobCheckConnectionConfig expectedInput = new JobCheckConnectionConfig().withConnectionConfiguration(CONFIG);
    when(job.getConfig().getConfigType()).thenReturn(value);
    when(job.getConfig().getCheckConnection()).thenReturn(expectedInput);

    factory.create(job);

    final ArgumentCaptor<WorkerRunFactory<JobCheckConnectionConfig>> argument = ArgumentCaptor.forClass(CheckConnectionWorkerRunFactory.class);
    verify(creator).create(eq(workspaceRoot), eq(pbf), argument.capture(), eq(JOB_ID), eq(ATTEMPT_ID), eq(expectedInput));
    Assertions.assertTrue(argument.getValue() instanceof CheckConnectionWorkerRunFactory);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSchema() {
    final JobDiscoverCatalogConfig expectedInput = new JobDiscoverCatalogConfig().withConnectionConfiguration(CONFIG);
    when(job.getConfig().getConfigType()).thenReturn(JobConfig.ConfigType.DISCOVER_SCHEMA);
    when(job.getConfig().getDiscoverCatalog()).thenReturn(expectedInput);

    factory.create(job);

    final ArgumentCaptor<WorkerRunFactory<JobDiscoverCatalogConfig>> argument = ArgumentCaptor.forClass(WorkerRunFactory.class);
    verify(creator).create(eq(workspaceRoot), eq(pbf), argument.capture(), eq(JOB_ID), eq(ATTEMPT_ID), eq(expectedInput));
    Assertions.assertTrue(argument.getValue() instanceof DiscoverWorkerRunFactory);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSync() {
    final JobSyncConfig expectedInput = new JobSyncConfig()
        .withState(new State().withState(STATE))
        .withSourceDockerImage("airbyte/source-earth:0.1.0")
        .withDestinationDockerImage("airbyte/destination-moon:0.1.0")
        .withSourceConfiguration(CONFIG)
        .withDestinationConfiguration(CONFIG2)
        .withConfiguredAirbyteCatalog(CONFIGURED_CATALOG);

    when(job.getConfig().getConfigType()).thenReturn(JobConfig.ConfigType.SYNC);
    when(job.getConfig().getSync()).thenReturn(expectedInput);

    factory.create(job);

    final ArgumentCaptor<WorkerRunFactory<JobSyncConfig>> argument = ArgumentCaptor.forClass(WorkerRunFactory.class);
    verify(creator).create(eq(workspaceRoot), eq(pbf), argument.capture(), eq(JOB_ID), eq(ATTEMPT_ID), eq(expectedInput));
    Assertions.assertTrue(argument.getValue() instanceof SyncWorkerRunFactory);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testResetConnection() {
    final JobResetConnectionConfig expectedInput = new JobResetConnectionConfig()
        .withDestinationDockerImage("airbyte/destination-moon:0.1.0")
        .withDestinationConfiguration(CONFIG2)
        .withConfiguredAirbyteCatalog(CONFIGURED_CATALOG);

    when(job.getConfig().getConfigType()).thenReturn(JobConfig.ConfigType.RESET_CONNECTION);
    when(job.getConfig().getResetConnection()).thenReturn(expectedInput);

    factory.create(job);

    final ArgumentCaptor<WorkerRunFactory<JobResetConnectionConfig>> argument = ArgumentCaptor.forClass(WorkerRunFactory.class);
    verify(creator).create(eq(workspaceRoot), eq(pbf), argument.capture(), eq(JOB_ID), eq(ATTEMPT_ID), eq(expectedInput));
    Assertions.assertTrue(argument.getValue() instanceof ResetConnectionWorkerRunFactory);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testGetSpec() {
    when(job.getConfig().getConfigType()).thenReturn(JobConfig.ConfigType.GET_SPEC);
    final JobGetSpecConfig expectedConfig = new JobGetSpecConfig().withDockerImage("notarealimage");
    when(job.getConfig().getGetSpec()).thenReturn(expectedConfig);

    factory.create(job);

    final ArgumentCaptor<WorkerRunFactory<JobGetSpecConfig>> argument = ArgumentCaptor.forClass(WorkerRunFactory.class);
    verify(creator).create(eq(workspaceRoot), eq(pbf), argument.capture(), eq(JOB_ID), eq(ATTEMPT_ID), eq(expectedConfig));

    Assertions.assertTrue(argument.getValue() instanceof GetSpecWorkerRunFactory);
  }

}
