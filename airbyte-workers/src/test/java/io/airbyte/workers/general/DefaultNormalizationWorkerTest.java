/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.workers.TestConfigHelpers;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.internal.AirbyteMessageUtils;
import io.airbyte.workers.normalization.NormalizationRunner;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultNormalizationWorkerTest {

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;
  private static final Path WORKSPACE_ROOT = Path.of("workspaces/10");
  private static final AirbyteTraceMessage ERROR_TRACE_MESSAGE =
      AirbyteMessageUtils.createErrorTraceMessage("a normalization error occurred", 123.0);

  private WorkerConfigs workerConfigs;
  private Path jobRoot;
  private Path normalizationRoot;
  private NormalizationInput normalizationInput;
  private NormalizationRunner normalizationRunner;

  @BeforeEach
  void setup() throws Exception {
    workerConfigs = new WorkerConfigs(new EnvConfigs());
    jobRoot = Files.createDirectories(Files.createTempDirectory("test").resolve(WORKSPACE_ROOT));
    normalizationRoot = jobRoot.resolve("normalize");

    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    normalizationInput = new NormalizationInput()
        .withDestinationConfiguration(syncPair.getValue().getDestinationConfiguration())
        .withCatalog(syncPair.getValue().getCatalog())
        .withResourceRequirements(workerConfigs.getResourceRequirements());

    normalizationRunner = mock(NormalizationRunner.class);

    when(normalizationRunner.normalize(
        JOB_ID,
        JOB_ATTEMPT,
        normalizationRoot,
        normalizationInput.getDestinationConfiguration(),
        normalizationInput.getCatalog(), workerConfigs.getResourceRequirements()))
            .thenReturn(true);
  }

  @Test
  void test() throws Exception {
    final DefaultNormalizationWorker normalizationWorker =
        new DefaultNormalizationWorker(JOB_ID, JOB_ATTEMPT, normalizationRunner, WorkerEnvironment.DOCKER);

    final NormalizationSummary normalizationOutput = normalizationWorker.run(normalizationInput, jobRoot);

    verify(normalizationRunner).start();
    verify(normalizationRunner).normalize(
        JOB_ID,
        JOB_ATTEMPT,
        normalizationRoot,
        normalizationInput.getDestinationConfiguration(),
        normalizationInput.getCatalog(), workerConfigs.getResourceRequirements());
    verify(normalizationRunner).close();
    assertNotNull(normalizationOutput.getStartTime());
    assertNotNull(normalizationOutput.getEndTime());
  }

  // This test verifies the expected behaviour prior to adding TRACE message handling
  // if no TRACE messages are emitted we should throw a WorkerException as before
  @Test
  void testFailure() throws Exception {
    when(normalizationRunner.normalize(JOB_ID,
        JOB_ATTEMPT,
        normalizationRoot,
        normalizationInput.getDestinationConfiguration(),
        normalizationInput.getCatalog(), workerConfigs.getResourceRequirements()))
            .thenReturn(false);

    final DefaultNormalizationWorker normalizationWorker =
        new DefaultNormalizationWorker(JOB_ID, JOB_ATTEMPT, normalizationRunner, WorkerEnvironment.DOCKER);

    assertThrows(WorkerException.class, () -> normalizationWorker.run(normalizationInput, jobRoot));

    verify(normalizationRunner).start();
  }

  // This test verifies failure behaviour when we have TRACE messages emitted from normalization
  // instead of throwing an exception, we should return the summary with a non-empty FailureReasons
  // array
  @Test
  void testFailureWithTraceMessage() throws Exception {
    when(normalizationRunner.normalize(JOB_ID,
        JOB_ATTEMPT,
        normalizationRoot,
        normalizationInput.getDestinationConfiguration(),
        normalizationInput.getCatalog(), workerConfigs.getResourceRequirements()))
            .thenReturn(false);

    when(normalizationRunner.getTraceMessages()).thenReturn(Stream.of(ERROR_TRACE_MESSAGE));

    final DefaultNormalizationWorker normalizationWorker =
        new DefaultNormalizationWorker(JOB_ID, JOB_ATTEMPT, normalizationRunner, WorkerEnvironment.DOCKER);

    final NormalizationSummary normalizationOutput = normalizationWorker.run(normalizationInput, jobRoot);

    verify(normalizationRunner).start();
    verify(normalizationRunner).normalize(
        JOB_ID,
        JOB_ATTEMPT,
        normalizationRoot,
        normalizationInput.getDestinationConfiguration(),
        normalizationInput.getCatalog(), workerConfigs.getResourceRequirements());
    verify(normalizationRunner).close();
    assertNotNull(normalizationOutput.getStartTime());
    assertNotNull(normalizationOutput.getEndTime());
    assertFalse(normalizationOutput.getFailures().isEmpty());
    assertTrue(normalizationOutput.getFailures().stream()
        .anyMatch(f -> f.getFailureOrigin().equals(FailureOrigin.NORMALIZATION)
            && f.getExternalMessage().contains(ERROR_TRACE_MESSAGE.getError().getMessage())));
  }

}
