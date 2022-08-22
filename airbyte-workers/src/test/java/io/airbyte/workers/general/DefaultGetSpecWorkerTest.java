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
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.FailureReason;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.internal.AirbyteMessageUtils;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultGetSpecWorkerTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String DUMMY_IMAGE_NAME = "airbyte/notarealimage:1.1";

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

    worker = new DefaultGetSpecWorker(new WorkerConfigs(new EnvConfigs()), integrationLauncher);
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
  void testFailureOnInvalidSpec() throws InterruptedException {
    final String expectedSpecString = "{\"key\":\"value\"}";
    when(process.getInputStream()).thenReturn(new ByteArrayInputStream(expectedSpecString.getBytes(Charsets.UTF_8)));
    when(process.waitFor(anyLong(), any())).thenReturn(true);
    when(process.exitValue()).thenReturn(0);

    assertThatThrownBy(() -> worker.run(config, jobRoot))
        .isInstanceOf(WorkerException.class)
        .getCause()
        .isInstanceOf(WorkerException.class)
        .hasMessageContaining("integration failed to output a spec struct.")
        .hasNoCause();
  }

  @Test
  void testFailureOnNonzeroExitCode() throws InterruptedException, IOException {
    final String expectedSpecString = MoreResources.readResource("valid_spec.json");

    final AirbyteMessage message = new AirbyteMessage()
        .withType(Type.SPEC)
        .withSpec(Jsons.deserialize(expectedSpecString, io.airbyte.protocol.models.ConnectorSpecification.class));

    when(process.getInputStream()).thenReturn(new ByteArrayInputStream(Jsons.serialize(message).getBytes(Charsets.UTF_8)));
    when(process.waitFor(anyLong(), any())).thenReturn(true);
    when(process.exitValue()).thenReturn(1);

    assertThatThrownBy(() -> worker.run(config, jobRoot))
        .isInstanceOf(WorkerException.class)
        .getCause()
        .isInstanceOf(WorkerException.class)
        .hasMessageContaining("Spec job subprocess finished with exit code")
        .hasNoCause();
  }

  @Test
  void testFailureOnNonzeroExitCodeWithTraceMessage() throws WorkerException, InterruptedException {
    final AirbyteMessage message = AirbyteMessageUtils.createTraceMessage("some error from the connector", 123.0);

    when(process.getInputStream()).thenReturn(new ByteArrayInputStream(Jsons.serialize(message).getBytes(Charsets.UTF_8)));
    when(process.waitFor(anyLong(), any())).thenReturn(true);
    when(process.exitValue()).thenReturn(1);

    final ConnectorJobOutput output = worker.run(config, jobRoot);
    assertEquals(OutputType.SPEC, output.getOutputType());
    assertNull(output.getSpec());
    assertNotNull(output.getFailureReason());

    final FailureReason failureReason = output.getFailureReason();
    assertEquals("some error from the connector", failureReason.getExternalMessage());
  }

}
