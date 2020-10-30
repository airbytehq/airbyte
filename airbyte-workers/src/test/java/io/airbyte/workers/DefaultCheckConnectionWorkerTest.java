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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.protocols.airbyte.AirbyteStreamFactory;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DefaultCheckConnectionWorkerTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final JsonNode CREDS = Jsons.jsonNode(ImmutableMap.builder().put("apiKey", "123").build());

  private Path jobRoot;
  private StandardCheckConnectionInput input;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private AirbyteStreamFactory successStreamFactory;
  private AirbyteStreamFactory failureStreamFactory;

  @BeforeEach
  public void setup() throws IOException, WorkerException {
    input = new StandardCheckConnectionInput().withConnectionConfiguration(CREDS);

    jobRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "");
    integrationLauncher = mock(IntegrationLauncher.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class);

    when(integrationLauncher.check(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME).start()).thenReturn(process);
    final InputStream inputStream = mock(InputStream.class);
    when(process.getInputStream()).thenReturn(inputStream);
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream(new byte[0]));

    final AirbyteMessage successMessage = new AirbyteMessage()
        .withType(Type.CONNECTION_STATUS)
        .withConnectionStatus(new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED));
    successStreamFactory = noop -> Lists.newArrayList(successMessage).stream();

    final AirbyteMessage failureMessage = new AirbyteMessage()
        .withType(Type.CONNECTION_STATUS)
        .withConnectionStatus(new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage("failed to connect"));
    failureStreamFactory = noop -> Lists.newArrayList(failureMessage).stream();
  }

  @Test
  public void testEnums() {
    Enums.isCompatible(AirbyteConnectionStatus.Status.class, Status.class);
  }

  @Test
  public void testSuccessfulConnection() {
    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, successStreamFactory);
    final OutputAndStatus<StandardCheckConnectionOutput> output = worker.run(input, jobRoot);

    assertEquals(JobStatus.SUCCEEDED, output.getStatus());
    assertTrue(output.getOutput().isPresent());
    assertEquals(Status.SUCCEEDED, output.getOutput().get().getStatus());
    assertNull(output.getOutput().get().getMessage());

  }

  @Test
  public void testFailedConnection() {
    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, failureStreamFactory);
    final OutputAndStatus<StandardCheckConnectionOutput> output = worker.run(input, jobRoot);

    assertEquals(JobStatus.SUCCEEDED, output.getStatus());
    assertTrue(output.getOutput().isPresent());
    assertEquals(Status.FAILED, output.getOutput().get().getStatus());
    assertEquals("failed to connect", output.getOutput().get().getMessage());
  }

  @Test
  public void testProcessFail() {
    when(process.exitValue()).thenReturn(1);

    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, failureStreamFactory);
    final OutputAndStatus<StandardCheckConnectionOutput> output = worker.run(input, jobRoot);

    assertEquals(JobStatus.FAILED, output.getStatus());
    assertTrue(output.getOutput().isEmpty());
  }

  @Test
  public void testExceptionThrownInRun() throws WorkerException {
    doThrow(new RuntimeException()).when(integrationLauncher).check(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME);

    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, failureStreamFactory);
    final OutputAndStatus<StandardCheckConnectionOutput> output = worker.run(input, jobRoot);

    assertEquals(JobStatus.FAILED, output.getStatus());
    assertTrue(output.getOutput().isEmpty());
  }

  @Test
  public void testCancel() {
    DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, successStreamFactory);
    worker.run(input, jobRoot);

    worker.cancel();

    verify(process).destroy();
  }

}
