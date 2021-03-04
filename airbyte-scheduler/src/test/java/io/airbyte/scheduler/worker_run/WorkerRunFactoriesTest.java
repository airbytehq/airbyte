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
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.State;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.scheduler.worker_run.BaseWorkerRunFactory.IntegrationLauncherFactory;
import io.airbyte.scheduler.worker_run.BaseWorkerRunFactory.WorkerRunCreator;
import io.airbyte.workers.Worker;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.wrappers.JobOutputCheckConnectionWorker;
import io.airbyte.workers.wrappers.JobOutputDiscoverSchemaWorker;
import io.airbyte.workers.wrappers.JobOutputGetSpecWorker;
import io.airbyte.workers.wrappers.JobOutputSyncWorker;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;
import org.mockito.ArgumentCaptor;

/**
 * Tests the WorkerRunFactory for each job type. These are all in the same test class since they are
 * very similar and tend to use almost identical inputs.
 */
class WorkerRunFactoriesTest {

  private static final long JOB_ID = 1L;
  private static final int ATTEMPT_ID = 2;
  private static final JsonNode CONFIG = Jsons.jsonNode(1);
  private static final JsonNode CONFIG2 = Jsons.jsonNode(2);
  private static final JsonNode STATE = Jsons.emptyObject();
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = new ConfiguredAirbyteCatalog()
      .withStreams(Lists.newArrayList(new ConfiguredAirbyteStream().withSyncMode(SyncMode.FULL_REFRESH)));
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

  private Path jobRoot;
  private ProcessBuilderFactory pbf;
  private IntegrationLauncherFactory integrationLauncherFactory;
  private WorkerRunCreator workerRunCreator;

  @BeforeEach
  void setUp() throws IOException {
    integrationLauncherFactory = mock(IntegrationLauncherFactory.class);
    workerRunCreator = mock(WorkerRunCreator.class);

    final Path rootPath = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test");
    jobRoot = rootPath.resolve("abc");
    pbf = mock(ProcessBuilderFactory.class);
  }

  @SuppressWarnings("unchecked")
  @ParameterizedTest
  @EnumSource(value = ConfigType.class,
              names = {"CHECK_CONNECTION_SOURCE", "CHECK_CONNECTION_DESTINATION"})
  void testConnection(ConfigType value) {
    final JobCheckConnectionConfig config = new JobCheckConnectionConfig()
        .withDockerImage("airbyte/source-earth:0.1.0")
        .withConnectionConfiguration(CONFIG);
    final StandardCheckConnectionInput expectedInput =
        new StandardCheckConnectionInput().withConnectionConfiguration(config.getConnectionConfiguration());

    new CheckConnectionWorkerRunFactory(integrationLauncherFactory, workerRunCreator).create(jobRoot, pbf, JOB_ID, ATTEMPT_ID, config);
    final ArgumentCaptor<Worker<StandardCheckConnectionInput, JobOutput>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(workerRunCreator).create(eq(jobRoot), eq(expectedInput), argument.capture());
    verify(integrationLauncherFactory).create(JOB_ID, ATTEMPT_ID, config.getDockerImage(), pbf);
    Assertions.assertTrue(argument.getValue() instanceof JobOutputCheckConnectionWorker);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSchema() {
    final JobDiscoverCatalogConfig config = new JobDiscoverCatalogConfig()
        .withDockerImage("airbyte/source-earth:0.1.0")
        .withConnectionConfiguration(CONFIG);
    final StandardDiscoverCatalogInput expectedInput = new StandardDiscoverCatalogInput()
        .withConnectionConfiguration(config.getConnectionConfiguration());

    new DiscoverWorkerRunFactory(integrationLauncherFactory, workerRunCreator).create(jobRoot, pbf, JOB_ID, ATTEMPT_ID, config);
    final ArgumentCaptor<Worker<StandardDiscoverCatalogInput, JobOutput>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(workerRunCreator).create(eq(jobRoot), eq(expectedInput), argument.capture());
    verify(integrationLauncherFactory).create(JOB_ID, ATTEMPT_ID, config.getDockerImage(), pbf);
    Assertions.assertTrue(argument.getValue() instanceof JobOutputDiscoverSchemaWorker);

  }

  @SuppressWarnings("unchecked")
  @Test
  void testSync() {
    final JobSyncConfig config = new JobSyncConfig()
        .withState(new State().withState(STATE))
        .withSourceDockerImage("airbyte/source-earth:0.1.0")
        .withDestinationDockerImage("airbyte/destination-moon:0.1.0")
        .withSourceConfiguration(CONFIG)
        .withDestinationConfiguration(CONFIG2)
        .withConfiguredAirbyteCatalog(CONFIGURED_CATALOG);

    final StandardSyncInput expectedInput = new StandardSyncInput()
        .withNamespaceDefault(config.getNamespaceDefault())
        .withSourceConfiguration(config.getSourceConfiguration())
        .withDestinationConfiguration(config.getDestinationConfiguration())
        .withCatalog(config.getConfiguredAirbyteCatalog())
        .withState(config.getState());

    new SyncWorkerRunFactory(integrationLauncherFactory, workerRunCreator)
        .create(jobRoot, pbf, JOB_ID, ATTEMPT_ID, config);

    final ArgumentCaptor<Worker<StandardSyncInput, JobOutput>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(workerRunCreator).create(eq(jobRoot), eq(expectedInput), argument.capture());
    verify(integrationLauncherFactory).create(JOB_ID, ATTEMPT_ID, config.getSourceDockerImage(), pbf);
    verify(integrationLauncherFactory).create(JOB_ID, ATTEMPT_ID, config.getDestinationDockerImage(), pbf);
    Assertions.assertTrue(argument.getValue() instanceof JobOutputSyncWorker);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testResetConnection() {
    final JobResetConnectionConfig config = new JobResetConnectionConfig()
        .withDestinationDockerImage("airbyte/destination-moon:0.1.0")
        .withDestinationConfiguration(CONFIG2)
        .withConfiguredAirbyteCatalog(CONFIGURED_CATALOG);

    final StandardSyncInput expectedInput = new StandardSyncInput()
        .withNamespaceDefault(job.getConfig().getSync().getNamespaceDefault())
        .withSourceConfiguration(Jsons.emptyObject())
        .withDestinationConfiguration(config.getDestinationConfiguration())
        .withCatalog(config.getConfiguredAirbyteCatalog());

    new ResetConnectionWorkerRunFactory(integrationLauncherFactory, workerRunCreator)
        .create(jobRoot, pbf, JOB_ID, ATTEMPT_ID, config);

    final ArgumentCaptor<Worker<StandardSyncInput, JobOutput>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(workerRunCreator).create(eq(jobRoot), eq(expectedInput), argument.capture());
    verify(integrationLauncherFactory).create(JOB_ID, ATTEMPT_ID, config.getDestinationDockerImage(), pbf);
    Assertions.assertTrue(argument.getValue() instanceof JobOutputSyncWorker);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testGetSpec() {
    final JobGetSpecConfig expectedConfig = new JobGetSpecConfig().withDockerImage("notarealimage");

    new GetSpecWorkerRunFactory(integrationLauncherFactory, workerRunCreator).create(jobRoot, pbf, JOB_ID, ATTEMPT_ID, expectedConfig);

    verify(integrationLauncherFactory).create(JOB_ID, ATTEMPT_ID, expectedConfig.getDockerImage(), pbf);
    final ArgumentCaptor<Worker<JobGetSpecConfig, JobOutput>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(workerRunCreator).create(eq(jobRoot), eq(expectedConfig), argument.capture());
    Assertions.assertTrue(argument.getValue() instanceof JobOutputGetSpecWorker);
  }

}
