/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

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
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class DefaultCheckConnectionWorkerTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final JsonNode CREDS = Jsons.jsonNode(ImmutableMap.builder().put("apiKey", "123").build());

  private Path jobRoot;
  private StandardCheckConnectionInput input;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private AirbyteStreamFactory successStreamFactory;
  private AirbyteStreamFactory failureStreamFactory;
  private AirbyteStreamFactory traceMessageStreamFactory;

  @BeforeEach
  void setup() throws IOException, WorkerException {
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

    final AirbyteMessage traceMessage = AirbyteMessageUtils.createErrorMessage("some error from the connector", 123.0);
    traceMessageStreamFactory = noop -> Lists.newArrayList(traceMessage).stream();
  }

  @Test
  void testEnums() {
    Enums.isCompatible(AirbyteConnectionStatus.Status.class, Status.class);
  }

  @Test
  void testSuccessfulConnection() throws WorkerException {
    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, successStreamFactory);
    final ConnectorJobOutput output = worker.run(input, jobRoot);

    assertEquals(output.getOutputType(), OutputType.CHECK_CONNECTION);
    assertNull(output.getFailureReason());

    final StandardCheckConnectionOutput checkOutput = output.getCheckConnection();
    assertEquals(Status.SUCCEEDED, checkOutput.getStatus());
    assertNull(checkOutput.getMessage());
  }

  @Test
  void testFailedConnection() throws WorkerException {
    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, failureStreamFactory);
    final ConnectorJobOutput output = worker.run(input, jobRoot);

    assertEquals(output.getOutputType(), OutputType.CHECK_CONNECTION);
    assertNull(output.getFailureReason());

    final StandardCheckConnectionOutput checkOutput = output.getCheckConnection();
    assertEquals(Status.FAILED, checkOutput.getStatus());
    assertEquals("failed to connect", checkOutput.getMessage());
  }

  @Test
  void testProcessFail() {
    when(process.exitValue()).thenReturn(1);

    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, failureStreamFactory);
    assertThrows(WorkerException.class, () -> worker.run(input, jobRoot));
  }

  @Test
  void testProcessFailWithTraceMessage() throws WorkerException {
    when(process.exitValue()).thenReturn(1);

    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, traceMessageStreamFactory);
    final ConnectorJobOutput output = worker.run(input, jobRoot);

    assertEquals(output.getOutputType(), OutputType.CHECK_CONNECTION);
    assertNull(output.getCheckConnection());

    final FailureReason failureReason = output.getFailureReason();
    assertEquals("some error from the connector", failureReason.getExternalMessage());
  }

  @Test
  void testExceptionThrownInRun() throws WorkerException {
    doThrow(new RuntimeException()).when(integrationLauncher).check(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME, Jsons.serialize(CREDS));

    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, failureStreamFactory);

    assertThrows(WorkerException.class, () -> worker.run(input, jobRoot));
  }

  @Test
  void testCancel() throws WorkerException {
    final DefaultCheckConnectionWorker worker = new DefaultCheckConnectionWorker(integrationLauncher, successStreamFactory);
    worker.run(input, jobRoot);

    worker.cancel();

    verify(process).destroy();
  }

}
