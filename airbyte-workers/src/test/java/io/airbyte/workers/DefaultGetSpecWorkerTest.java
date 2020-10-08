package io.airbyte.workers;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.workers.process.ProcessBuilderFactory;
import org.junit.Before;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.testcontainers.shaded.org.bouncycastle.pqc.crypto.ExchangePair;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.StringBufferInputStream;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class DefaultGetSpecWorkerTest {

  private static final String DUMMY_IMAGE_NAME = "airbyte/notarealimage:1.1";

  private DefaultGetSpecWorker worker;
  private ProcessBuilderFactory pbf;
  private Process process;
  private Path jobRoot;
  private JobGetSpecConfig config;

  @BeforeEach
  public void setup() throws IOException {
    config = new JobGetSpecConfig().withDockerImage(DUMMY_IMAGE_NAME);
    pbf = mock(ProcessBuilderFactory.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class);
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream(new byte[0]));
    jobRoot = Files.createTempDirectory("");
    worker = new DefaultGetSpecWorker(pbf);
  }

  @Test
  public void testSuccessfulRun() throws WorkerException, IOException, InterruptedException {
    String expectedSpecString = MoreResources.readResource("valid_spec.json");
    when(process.getInputStream()).thenReturn(new ByteArrayInputStream(expectedSpecString.getBytes()));
    when(process.waitFor(anyLong(), any())).thenReturn(true);
    when(process.exitValue()).thenReturn(0);
    when(pbf.create(jobRoot, DUMMY_IMAGE_NAME, "--spec").start()).thenReturn(process);

    OutputAndStatus<StandardGetSpecOutput> actualOutput = worker.run(config, jobRoot);
    OutputAndStatus<StandardGetSpecOutput> expectedOutput =
        new OutputAndStatus<>(JobStatus.SUCCESSFUL,
            new StandardGetSpecOutput().withSpecification(Jsons.deserialize(expectedSpecString, ConnectorSpecification.class))
        );

    assertEquals(expectedOutput, actualOutput);
  }

  @Test
  public void testFailureOnInvalidSpec() throws InterruptedException, WorkerException, IOException {
    String expectedSpecString = MoreResources.readResource("invalid_spec.json");
    when(process.getInputStream()).thenReturn(new ByteArrayInputStream(expectedSpecString.getBytes()));
    when(process.waitFor(anyLong(), any())).thenReturn(true);
    when(process.exitValue()).thenReturn(0);
    when(pbf.create(jobRoot, DUMMY_IMAGE_NAME, "--spec").start()).thenReturn(process);

    OutputAndStatus<StandardGetSpecOutput> actualOutput = worker.run(config, jobRoot);
    OutputAndStatus<StandardGetSpecOutput> expectedOutput = new OutputAndStatus<>(JobStatus.FAILED);
    assertEquals(expectedOutput, actualOutput);
  }

  @Test
  public void testFailureOnNonzeroExitCode() throws InterruptedException, WorkerException, IOException {
    when(process.waitFor(anyLong(), any())).thenReturn(true);
    when(process.exitValue()).thenReturn(1);
    when(pbf.create(jobRoot, DUMMY_IMAGE_NAME, "--spec").start()).thenReturn(process);

    OutputAndStatus<StandardGetSpecOutput> actualOutput = worker.run(config, jobRoot);
    OutputAndStatus<StandardGetSpecOutput> expectedOutput = new OutputAndStatus<>(JobStatus.FAILED);

    assertEquals(expectedOutput, actualOutput);
  }
}
