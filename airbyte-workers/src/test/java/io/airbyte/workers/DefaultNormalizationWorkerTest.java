/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.workers.normalization.NormalizationRunner;
import java.nio.file.Files;
import java.nio.file.Path;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultNormalizationWorkerTest {

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;
  private static final Path WORKSPACE_ROOT = Path.of("workspaces/10");

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

}
