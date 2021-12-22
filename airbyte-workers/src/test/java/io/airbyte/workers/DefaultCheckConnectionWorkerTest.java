/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
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
import io.airbyte.config.EnvConfigs;
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

  private WorkerConfigs workerConfigs;
  private Path jobRoot;
  private StandardCheckConnectionInput input;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private AirbyteStreamFactory successStreamFactory;
  private AirbyteStreamFactory failureStreamFactory;

  @BeforeEach
  public void setup() throws IOException, WorkerException {
    workerConfigs = new WorkerConfigs(new EnvConfigs());
    input = new StandardCheckConnectionInput().withConnectionConfiguration(CREDS);

    jobRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "");
    integrationLauncher = mock(IntegrationLauncher.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class);

    when(integrationLauncher.check(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME, Jsons.serialize(CREDS))).thenReturn(process);
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
  public void testSuccessfulConnection() throws WorkerException {
    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(workerConfigs, integrationLauncher, successStreamFactory);
    final StandardCheckConnectionOutput output = worker.run(input, jobRoot);

    assertEquals(Status.SUCCEEDED, output.getStatus());
    assertNull(output.getMessage());

  }

  @Test
  public void testFailedConnection() throws WorkerException {
    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(workerConfigs, integrationLauncher, failureStreamFactory);
    final StandardCheckConnectionOutput output = worker.run(input, jobRoot);

    assertEquals(Status.FAILED, output.getStatus());
    assertEquals("failed to connect", output.getMessage());
  }

  @Test
  public void testProcessFail() {
    when(process.exitValue()).thenReturn(1);

    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(workerConfigs, integrationLauncher, failureStreamFactory);
    assertThrows(WorkerException.class, () -> worker.run(input, jobRoot));
  }

  @Test
  public void testExceptionThrownInRun() throws WorkerException {
    doThrow(new RuntimeException()).when(integrationLauncher).check(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME, Jsons.serialize(CREDS));

    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(workerConfigs, integrationLauncher, failureStreamFactory);
    assertThrows(WorkerException.class, () -> worker.run(input, jobRoot));
  }

  @Test
  public void testCancel() throws WorkerException {
    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(workerConfigs, integrationLauncher, successStreamFactory);
    worker.run(input, jobRoot);

    worker.cancel();

    verify(process).destroy();
  }

}
