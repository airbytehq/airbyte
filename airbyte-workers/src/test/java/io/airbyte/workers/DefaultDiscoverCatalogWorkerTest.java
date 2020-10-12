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

package io.airbyte.workers;

import static org.junit.Assert.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DefaultDiscoverCatalogWorkerTest {

  private static final JsonNode CREDENTIALS = Jsons.jsonNode(ImmutableMap.builder().put("apiKey", "123").build());

  private Path jobRoot;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private StandardDiscoverCatalogInput input;

  @BeforeEach
  public void setup() throws Exception {
    jobRoot = Files.createTempDirectory("");
    integrationLauncher = mock(IntegrationLauncher.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class);

    input = new StandardDiscoverCatalogInput().withConnectionConfiguration(CREDENTIALS);

    when(integrationLauncher.discover(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME)
        .redirectOutput(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME).toFile())
        .start())
            .thenReturn(process);
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("data".getBytes(StandardCharsets.UTF_8)));
    IOs.writeFile(jobRoot, WorkerConstants.CATALOG_JSON_FILENAME, MoreResources.readResource("simple_postgres_singer_catalog.json"));
  }

  @SuppressWarnings("BusyWait")
  @Test
  public void testDiscoverSchema() throws Exception {
    final DefaultDiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(integrationLauncher);
    final OutputAndStatus<StandardDiscoverCatalogOutput> output = worker.run(input, jobRoot);

    final OutputAndStatus<StandardDiscoverCatalogOutput> expectedOutput =
        new OutputAndStatus<>(
            JobStatus.SUCCESSFUL,
            Jsons.deserialize(MoreResources.readResource("simple_discovered_postgres_catalog_output.json"), StandardDiscoverCatalogOutput.class));

    assertEquals(expectedOutput, output);

    assertTrue(Files.exists(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME)));

    assertEquals(
        Jsons.jsonNode(input.getConnectionConfiguration()),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME)));

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).waitFor(anyLong(), any());
  }

  @SuppressWarnings("BusyWait")
  @Test
  public void testDiscoverSchemaProcessFail() throws Exception {
    when(process.exitValue()).thenReturn(1);

    final DefaultDiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(integrationLauncher);
    final OutputAndStatus<StandardDiscoverCatalogOutput> output = worker.run(input, jobRoot);

    final OutputAndStatus<StandardDiscoverCatalogOutput> expectedOutput = new OutputAndStatus<>(JobStatus.FAILED);

    assertEquals(expectedOutput, output);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).waitFor(anyLong(), any());
  }

  @Test
  public void testDiscoverSchemaException() throws WorkerException {
    when(integrationLauncher.discover(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME))
        .thenThrow(new RuntimeException());

    final DefaultDiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(integrationLauncher);
    final OutputAndStatus<StandardDiscoverCatalogOutput> output = worker.run(input, jobRoot);

    final OutputAndStatus<StandardDiscoverCatalogOutput> expectedOutput = new OutputAndStatus<>(JobStatus.FAILED);

    assertEquals(expectedOutput, output);
  }

  @Test
  public void testCancel() {
    DefaultDiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(integrationLauncher);
    worker.run(input, jobRoot);

    worker.cancel();

    verify(process).destroy();
  }

}
