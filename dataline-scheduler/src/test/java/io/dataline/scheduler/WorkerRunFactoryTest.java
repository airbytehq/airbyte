/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.scheduler;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.dataline.commons.json.Jsons;
import io.dataline.config.JobConfig;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardSyncInput;
import io.dataline.workers.CheckConnectionWorker;
import io.dataline.workers.DiscoverSchemaWorker;
import io.dataline.workers.SyncWorker;
import io.dataline.workers.Worker;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;
import org.mockito.ArgumentCaptor;

class WorkerRunFactoryTest {

  private static JsonNode CONFIG = Jsons.jsonNode(1);

  private Job job;
  private Path rootPath;
  private WorkerRunFactory.Creator creator;

  private WorkerRunFactory factory;

  @BeforeEach
  void setUp() throws IOException {
    job = mock(Job.class, RETURNS_DEEP_STUBS);
    when(job.getId()).thenReturn(1L);

    creator = mock(WorkerRunFactory.Creator.class);
    rootPath = Files.createTempDirectory("test");

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

    StandardCheckConnectionInput expectedInput = new StandardCheckConnectionInput().withConnectionConfiguration(CONFIG);
    ArgumentCaptor<Worker<StandardCheckConnectionInput, ?>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(creator).create(eq(rootPath.resolve("1")), eq(expectedInput), argument.capture(), any());
    assertTrue(argument.getValue() instanceof CheckConnectionWorker);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSchema() {
    when(job.getConfig().getConfigType()).thenReturn(JobConfig.ConfigType.DISCOVER_SCHEMA);
    when(job.getConfig().getDiscoverSchema().getConnectionConfiguration()).thenReturn(CONFIG);

    factory.create(job);

    StandardDiscoverSchemaInput expectedInput = new StandardDiscoverSchemaInput().withConnectionConfiguration(CONFIG);
    ArgumentCaptor<Worker<StandardDiscoverSchemaInput, ?>> workerArg = ArgumentCaptor.forClass(Worker.class);
    verify(creator).create(eq(rootPath.resolve("1")), eq(expectedInput), workerArg.capture(), any());
    assertTrue(workerArg.getValue() instanceof DiscoverSchemaWorker);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSync() {
    when(job.getConfig().getConfigType()).thenReturn(JobConfig.ConfigType.SYNC);

    factory.create(job);

    StandardSyncInput expectedInput = new StandardSyncInput()
        .withSourceConnectionImplementation(job.getConfig().getSync().getSourceConnectionImplementation())
        .withDestinationConnectionImplementation(job.getConfig().getSync().getDestinationConnectionImplementation())
        .withStandardSync(job.getConfig().getSync().getStandardSync());

    ArgumentCaptor<Worker<StandardSyncInput, ?>> argument = ArgumentCaptor.forClass(Worker.class);
    verify(creator).create(eq(rootPath.resolve("1")), eq(expectedInput), argument.capture(), any());
    assertTrue(argument.getValue() instanceof SyncWorker);
  }

}
