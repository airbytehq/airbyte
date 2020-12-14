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

package io.airbyte.scheduler;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
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

class WorkerRunFactoryTest {

  private static final JsonNode CONFIG = Jsons.jsonNode(1);
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

  private Job job;
  private Path rootPath;
  private WorkerRunFactory.Creator creator;

  private WorkerRunFactory factory;

  @BeforeEach
  void setUp() throws IOException {
    job = mock(Job.class, RETURNS_DEEP_STUBS);
    when(job.getId()).thenReturn(1L);
    when(job.getAttemptsCount()).thenReturn(2);
    when(job.getConfig().getSync().getSourceDockerImage()).thenReturn("airbyte/source-earth:0.1.0");
    when(job.getConfig().getSync().getDestinationDockerImage()).thenReturn("airbyte/destination-moon:0.1.0");

    creator = mock(WorkerRunFactory.Creator.class);
    rootPath = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test");

    factory = new WorkerRunFactory(rootPath, mock(ProcessBuilderFactory.class), creator);
  }

  @SuppressWarnings("unchecked")
  @ParameterizedTest
  @EnumSource(value = JobConfig.ConfigType.class,
              names = {"CHECK_CONNECTION_SOURCE", "CHECK_CONNECTION_DESTINATION"})
  void testConnection(JobConfig.ConfigType value) {
    when(job.getConfig().getConfigType()).thenReturn(value);
    when(job.getConfig().getCheckConnection().getConnectionConfiguration()).thenReturn(CONFIG);

    factory.create(job);

    final StandardCheckConnectionInput expectedInput = new StandardCheckConnectionInput().withConnectionConfiguration(CONFIG);
    final ArgumentCaptor<Worker<StandardCheckConnectionInput, JobOutput>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(creator).create(eq(rootPath.resolve("1").resolve("2")), eq(expectedInput), argument.capture());
    Assertions.assertTrue(argument.getValue() instanceof JobOutputCheckConnectionWorker);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSchema() {
    when(job.getConfig().getConfigType()).thenReturn(JobConfig.ConfigType.DISCOVER_SCHEMA);
    when(job.getConfig().getDiscoverCatalog().getConnectionConfiguration()).thenReturn(CONFIG);

    factory.create(job);

    final StandardDiscoverCatalogInput expectedInput = new StandardDiscoverCatalogInput().withConnectionConfiguration(CONFIG);
    final ArgumentCaptor<Worker<StandardDiscoverCatalogInput, JobOutput>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(creator).create(eq(rootPath.resolve("1").resolve("2")), eq(expectedInput), argument.capture());
    Assertions.assertTrue(argument.getValue() instanceof JobOutputDiscoverSchemaWorker);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSync() {
    when(job.getConfig().getConfigType()).thenReturn(JobConfig.ConfigType.SYNC);

    factory.create(job);

    final StandardSyncInput expectedInput = new StandardSyncInput()
        .withSourceConfiguration(job.getConfig().getSync().getSourceConfiguration())
        .withDestinationConfiguration(job.getConfig().getSync().getDestinationConfiguration())
        .withCatalog(job.getConfig().getSync().getConfiguredAirbyteCatalog())
        .withState(job.getConfig().getSync().getState());

    final ArgumentCaptor<Worker<StandardSyncInput, JobOutput>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(creator).create(eq(rootPath.resolve("1").resolve("2")), eq(expectedInput), argument.capture());
    Assertions.assertTrue(argument.getValue() instanceof JobOutputSyncWorker);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testGetSpec() {
    when(job.getConfig().getConfigType()).thenReturn(JobConfig.ConfigType.GET_SPEC);
    final JobGetSpecConfig expectedConfig = new JobGetSpecConfig().withDockerImage("notarealimage");
    when(job.getConfig().getGetSpec()).thenReturn(expectedConfig);

    factory.create(job);

    final ArgumentCaptor<Worker<JobGetSpecConfig, JobOutput>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(creator).create(eq(rootPath.resolve("1").resolve("2")), eq(expectedConfig), argument.capture());
    Assertions.assertTrue(argument.getValue() instanceof JobOutputGetSpecWorker);
  }

}
