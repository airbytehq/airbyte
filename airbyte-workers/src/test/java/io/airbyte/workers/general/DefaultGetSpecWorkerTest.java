/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.base.Charsets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultGetSpecWorkerTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String DUMMY_IMAGE_NAME = "airbyte/notarealimage:1.1";
  private static final String ERROR_MESSAGE = "some error from the connector";

  private DefaultGetSpecWorker worker;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private Path jobRoot;
  private JobGetSpecConfig config;

  @BeforeEach
  void setup() throws IOException, WorkerException {
    jobRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "");
    config = new JobGetSpecConfig().withDockerImage(DUMMY_IMAGE_NAME);
    integrationLauncher = mock(IntegrationLauncher.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class);
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream(new byte[0]));
    when(integrationLauncher.spec(jobRoot)).thenReturn(process);

    worker = new DefaultGetSpecWorker(integrationLauncher);
  }

  @Test
  void testSuccessfulRun() throws IOException, InterruptedException, WorkerException {
    final String expectedSpecString = MoreResources.readResource("valid_spec.json");

    final AirbyteMessage message = new AirbyteMessage()
        .withType(Type.SPEC)
        .withSpec(Jsons.deserialize(expectedSpecString, io.airbyte.protocol.models.ConnectorSpecification.class));

    when(process.getInputStream()).thenReturn(new ByteArrayInputStream(Jsons.serialize(message).getBytes(Charsets.UTF_8)));
    when(process.waitFor(anyLong(), any())).thenReturn(true);
    when(process.exitValue()).thenReturn(0);

    final ConnectorJobOutput actualOutput = worker.run(config, jobRoot);
    final ConnectorJobOutput expectedOutput = new ConnectorJobOutput().withOutputType(OutputType.SPEC)
        .withSpec(Jsons.deserialize(expectedSpecString, ConnectorSpecification.class));

    assertThat(actualOutput).isEqualTo(expectedOutput);
  }

  @Test
  void testFailureOnInvalidSpecAndNoFailureReason() throws InterruptedException {
    final String expectedSpecString = "{\"key\":\"value\"}";
    when(process.getInputStream()).thenReturn(new ByteArrayInputStream(expectedSpecString.getBytes(Charsets.UTF_8)));
    when(process.waitFor(anyLong(), any())).thenReturn(true);

    assertThatThrownBy(() -> worker.run(config, jobRoot))
        .isInstanceOf(WorkerException.class)
        .getCause()
        .isInstanceOf(WorkerException.class)
        .hasMessageContaining("Integration failed to output a spec struct and did not output a failure reason")
        .hasNoCause();
  }

  @Test
  void testWithInvalidSpecAndFailureReason() throws InterruptedException, WorkerException {
    final String expectedSpecString = "{\"key\":\"value\"}";

    final AirbyteMessage message = new AirbyteMessage()
        .withType(Type.SPEC)
        .withSpec(Jsons.deserialize(expectedSpecString, io.airbyte.protocol.models.ConnectorSpecification.class));
    final AirbyteMessage traceMessage = AirbyteMessageUtils.createErrorMessage(ERROR_MESSAGE, 123.0);

    when(process.getInputStream())
        .thenReturn(new ByteArrayInputStream((Jsons.serialize(message) + "\n" + Jsons.serialize(traceMessage)).getBytes(Charsets.UTF_8)));
    when(process.waitFor(anyLong(), any())).thenReturn(true);

    final ConnectorJobOutput output = worker.run(config, jobRoot);
    assertEquals(OutputType.SPEC, output.getOutputType());
    assertNull(output.getSpec());

    final FailureReason failureReason = output.getFailureReason();
    assertEquals(ERROR_MESSAGE, failureReason.getExternalMessage());
  }

  @Test
  void testWithValidSpecAndFailureReason() throws InterruptedException, WorkerException, IOException {
    final String expectedSpecString = MoreResources.readResource("valid_spec.json");

    final AirbyteMessage message = new AirbyteMessage()
        .withType(Type.SPEC)
        .withSpec(Jsons.deserialize(expectedSpecString, io.airbyte.protocol.models.ConnectorSpecification.class));
    final AirbyteMessage traceMessage = AirbyteMessageUtils.createErrorMessage(ERROR_MESSAGE, 123.0);

    when(process.getInputStream())
        .thenReturn(new ByteArrayInputStream((Jsons.serialize(message) + "\n" + Jsons.serialize(traceMessage)).getBytes(Charsets.UTF_8)));
    when(process.waitFor(anyLong(), any())).thenReturn(true);

    final ConnectorJobOutput output = worker.run(config, jobRoot);
    assertEquals(OutputType.SPEC, output.getOutputType());
    assertEquals(output.getSpec(), Jsons.deserialize(expectedSpecString, ConnectorSpecification.class));
    final FailureReason failureReason = output.getFailureReason();
    assertEquals(ERROR_MESSAGE, failureReason.getExternalMessage());
  }

  @Test
  void testFailureReasonWithTraceMessageOnly() throws WorkerException, InterruptedException {
    final AirbyteMessage message = AirbyteMessageUtils.createErrorMessage(ERROR_MESSAGE, 123.0);

    when(process.getInputStream()).thenReturn(new ByteArrayInputStream(Jsons.serialize(message).getBytes(Charsets.UTF_8)));
    when(process.waitFor(anyLong(), any())).thenReturn(true);

    final ConnectorJobOutput output = worker.run(config, jobRoot);
    assertEquals(OutputType.SPEC, output.getOutputType());
    assertNull(output.getSpec());
    assertNotNull(output.getFailureReason());

    final FailureReason failureReason = output.getFailureReason();
    assertEquals(ERROR_MESSAGE, failureReason.getExternalMessage());
  }

}
