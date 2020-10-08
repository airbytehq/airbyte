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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverSchemaInput;
import io.airbyte.config.StandardDiscoverSchemaOutput;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class SingerCheckConnectionWorkerTest {

  private static final JsonNode CREDS = Jsons.jsonNode(ImmutableMap.builder().put("apiKey", "123").build());

  private Path jobRoot;
  private StandardCheckConnectionInput input;
  private StandardDiscoverSchemaInput discoverInput;
  private DiscoverSchemaWorker discoverSchemaWorker;

  @BeforeEach
  public void setup() throws IOException {
    jobRoot = Files.createTempDirectory("");

    input = new StandardCheckConnectionInput().withConnectionConfiguration(CREDS);

    discoverInput = new StandardDiscoverSchemaInput().withConnectionConfiguration(CREDS);

    discoverSchemaWorker = mock(DiscoverSchemaWorker.class);
  }

  @Test
  public void testSuccessfulConnection() {
    OutputAndStatus<StandardDiscoverSchemaOutput> discoverOutput =
        new OutputAndStatus<>(JobStatus.SUCCESSFUL, mock(StandardDiscoverSchemaOutput.class));
    when(discoverSchemaWorker.run(discoverInput, jobRoot)).thenReturn(discoverOutput);

    final SingerCheckConnectionWorker worker = new SingerCheckConnectionWorker(discoverSchemaWorker);
    final OutputAndStatus<StandardCheckConnectionOutput> output = worker.run(input, jobRoot);

    assertEquals(JobStatus.SUCCESSFUL, output.getStatus());
    assertTrue(output.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.SUCCESS, output.getOutput().get().getStatus());
    assertNull(output.getOutput().get().getMessage());

    verify(discoverSchemaWorker).run(discoverInput, jobRoot);
  }

  @Test
  public void testFailedConnection() {
    OutputAndStatus<StandardDiscoverSchemaOutput> discoverOutput = new OutputAndStatus<>(JobStatus.FAILED, null);
    when(discoverSchemaWorker.run(discoverInput, jobRoot)).thenReturn(discoverOutput);

    final SingerCheckConnectionWorker worker = new SingerCheckConnectionWorker(discoverSchemaWorker);
    final OutputAndStatus<StandardCheckConnectionOutput> output = worker.run(input, jobRoot);

    assertEquals(JobStatus.FAILED, output.getStatus());
    assertTrue(output.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.FAILURE, output.getOutput().get().getStatus());
    assertEquals("Failed to connect.", output.getOutput().get().getMessage());

    verify(discoverSchemaWorker).run(discoverInput, jobRoot);
  }

  @Test
  public void testCancel() {
    OutputAndStatus<StandardDiscoverSchemaOutput> discoverOutput =
        new OutputAndStatus<>(JobStatus.SUCCESSFUL, new StandardDiscoverSchemaOutput());
    when(discoverSchemaWorker.run(discoverInput, jobRoot)).thenReturn(discoverOutput);

    final SingerCheckConnectionWorker worker = new SingerCheckConnectionWorker(discoverSchemaWorker);
    worker.run(input, jobRoot);
    worker.cancel();

    verify(discoverSchemaWorker).cancel();
  }

}
