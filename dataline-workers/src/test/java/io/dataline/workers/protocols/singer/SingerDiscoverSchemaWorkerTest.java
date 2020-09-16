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

package io.dataline.workers.protocols.singer;

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
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.commons.resources.MoreResources;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.WorkerConstants;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SingerDiscoverSchemaWorkerTest {

  private static final String IMAGE_NAME = "selfie:latest";
  private static final JsonNode CREDENTIALS = Jsons.jsonNode(ImmutableMap.builder().put("apiKey", "123").build());

  private Path jobRoot;
  private ProcessBuilderFactory pbf;
  private Process process;
  private StandardDiscoverSchemaInput input;

  @BeforeEach
  public void setup() throws Exception {
    jobRoot = Files.createTempDirectory("");
    pbf = mock(ProcessBuilderFactory.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class);

    input = new StandardDiscoverSchemaInput().withConnectionConfiguration(CREDENTIALS);

    when(pbf.create(jobRoot, IMAGE_NAME, "--config", WorkerConstants.TAP_CONFIG_JSON_FILENAME, "--discover")
        .redirectError(jobRoot.resolve(WorkerConstants.TAP_ERR_LOG).toFile())
        .redirectOutput(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME).toFile())
        .start())
            .thenReturn(process);
    IOs.writeFile(jobRoot, WorkerConstants.CATALOG_JSON_FILENAME, MoreResources.readResource("simple_postgres_singer_catalog.json"));
  }

  @Test
  public void testDiscoverSchema() throws Exception {
    final SingerDiscoverSchemaWorker worker = new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf);
    final OutputAndStatus<StandardDiscoverSchemaOutput> output = worker.run(input, jobRoot);

    final OutputAndStatus<StandardDiscoverSchemaOutput> expectedOutput =
        new OutputAndStatus<>(
            JobStatus.SUCCESSFUL,
            Jsons.deserialize(MoreResources.readResource("simple_discovered_postgres_schema.json"), StandardDiscoverSchemaOutput.class));

    assertEquals(expectedOutput, output);

    assertTrue(Files.exists(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME)));

    assertEquals(
        Jsons.jsonNode(input.getConnectionConfiguration()),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME)));

    verify(process).waitFor(anyLong(), any());
  }

  @Test
  public void testDiscoverSchemaProcessFail() throws Exception {
    when(process.exitValue()).thenReturn(1);

    final SingerDiscoverSchemaWorker worker = new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf);
    final OutputAndStatus<StandardDiscoverSchemaOutput> output = worker.run(input, jobRoot);

    final OutputAndStatus<StandardDiscoverSchemaOutput> expectedOutput = new OutputAndStatus<>(JobStatus.FAILED);

    assertEquals(expectedOutput, output);

    verify(process).waitFor(anyLong(), any());
  }

  @Test
  public void testDiscoverSchemaException() {
    when(pbf.create(any(), any(), any())).thenThrow(new RuntimeException());

    final SingerDiscoverSchemaWorker worker = new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf);
    final OutputAndStatus<StandardDiscoverSchemaOutput> output = worker.run(input, jobRoot);

    final OutputAndStatus<StandardDiscoverSchemaOutput> expectedOutput = new OutputAndStatus<>(JobStatus.FAILED);

    assertEquals(expectedOutput, output);
  }

  @Test
  public void testCancel() {
    SingerDiscoverSchemaWorker worker = new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf);
    worker.run(input, jobRoot);

    worker.cancel();

    verify(process).destroy();
  }

}
