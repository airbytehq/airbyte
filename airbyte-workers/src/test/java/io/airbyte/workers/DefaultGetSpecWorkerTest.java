/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.google.common.base.Charsets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class DefaultGetSpecWorkerTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String DUMMY_IMAGE_NAME = "airbyte/notarealimage:1.1";

  private DefaultGetSpecWorker worker;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private Path jobRoot;
  private JobGetSpecConfig config;

  @BeforeEach
  public void setup() throws IOException, WorkerException {
    jobRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "");
    config = new JobGetSpecConfig().withDockerImage(DUMMY_IMAGE_NAME);
    integrationLauncher = Mockito.mock(IntegrationLauncher.class, Mockito.RETURNS_DEEP_STUBS);
    process = Mockito.mock(Process.class);
    Mockito.when(process.getErrorStream()).thenReturn(new ByteArrayInputStream(new byte[0]));
    Mockito.when(integrationLauncher.spec(jobRoot)).thenReturn(process);

    worker = new DefaultGetSpecWorker(integrationLauncher);
  }

  @Test
  public void testSuccessfulRun() throws IOException, InterruptedException, WorkerException {
    final String expectedSpecString = MoreResources.readResource("valid_spec.json");

    final AirbyteMessage message = new AirbyteMessage()
        .withType(Type.SPEC)
        .withSpec(Jsons.deserialize(expectedSpecString, io.airbyte.protocol.models.ConnectorSpecification.class));

    Mockito.when(process.getInputStream()).thenReturn(new ByteArrayInputStream(Jsons.serialize(message).getBytes(Charsets.UTF_8)));
    Mockito.when(process.waitFor(Mockito.anyLong(), Mockito.any())).thenReturn(true);
    Mockito.when(process.exitValue()).thenReturn(0);

    final ConnectorSpecification actualOutput = worker.run(config, jobRoot);
    final ConnectorSpecification expectedOutput = Jsons.deserialize(expectedSpecString, ConnectorSpecification.class);

    Assertions.assertThat(actualOutput).isEqualTo(expectedOutput);
  }

  @Test
  public void testFailureOnInvalidSpec() throws InterruptedException {
    final String expectedSpecString = "{\"key\":\"value\"}";
    Mockito.when(process.getInputStream()).thenReturn(new ByteArrayInputStream(expectedSpecString.getBytes()));
    Mockito.when(process.waitFor(Mockito.anyLong(), Mockito.any())).thenReturn(true);
    Mockito.when(process.exitValue()).thenReturn(0);

    Assertions.assertThatThrownBy(() -> worker.run(config, jobRoot))
        .isInstanceOf(WorkerException.class)
        .getCause()
        .isInstanceOf(WorkerException.class)
        .hasMessageContaining("integration failed to output a spec struct.")
        .hasNoCause();
  }

  @Test
  public void testFailureOnNonzeroExitCode() throws InterruptedException, IOException {
    final String expectedSpecString = MoreResources.readResource("valid_spec.json");

    final AirbyteMessage message = new AirbyteMessage()
        .withType(Type.SPEC)
        .withSpec(Jsons.deserialize(expectedSpecString, io.airbyte.protocol.models.ConnectorSpecification.class));

    Mockito.when(process.getInputStream()).thenReturn(new ByteArrayInputStream(Jsons.serialize(message).getBytes(Charsets.UTF_8)));
    Mockito.when(process.waitFor(Mockito.anyLong(), Mockito.any())).thenReturn(true);
    Mockito.when(process.exitValue()).thenReturn(1);

    Assertions.assertThatThrownBy(() -> worker.run(config, jobRoot))
        .isInstanceOf(WorkerException.class)
        .getCause()
        .isInstanceOf(WorkerException.class)
        .hasMessageContaining("Spec job subprocess finished with exit code")
        .hasNoCause();
  }

}
