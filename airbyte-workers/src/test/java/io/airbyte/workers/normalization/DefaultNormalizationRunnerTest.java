/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import static io.airbyte.commons.logging.LoggingHelper.RESET;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.normalization.DefaultNormalizationRunner.DestinationType;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultNormalizationRunnerTest {

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;

  private static Path logJobRoot;

  static {
    try {
      logJobRoot = Files.createTempDirectory(Path.of("/tmp"), "mdc_test");
      LogClientSingleton.getInstance().setJobMdc(WorkerEnvironment.DOCKER, LogConfigs.EMPTY, logJobRoot);
    } catch (final IOException e) {
      e.printStackTrace();
    }
  }

  private WorkerConfigs workerConfigs;
  private Path jobRoot;
  private ProcessFactory processFactory;
  private Process process;
  private JsonNode config;
  private ConfiguredAirbyteCatalog catalog;

  @BeforeEach
  void setup() throws IOException, WorkerException {
    workerConfigs = new WorkerConfigs(new EnvConfigs());
    jobRoot = Files.createDirectories(Files.createTempDirectory("test"));
    processFactory = mock(ProcessFactory.class);
    process = mock(Process.class);

    config = mock(JsonNode.class);
    catalog = mock(ConfiguredAirbyteCatalog.class);

    final Map<String, String> files = ImmutableMap.of(
        WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME, Jsons.serialize(config),
        WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME, Jsons.serialize(catalog));

    when(processFactory.create(AirbyteIntegrationLauncher.NORMALIZE_STEP, JOB_ID, JOB_ATTEMPT, jobRoot,
        NormalizationRunnerFactory.BASE_NORMALIZATION_IMAGE_NAME, false, files, null,
        workerConfigs.getResourceRequirements(),
        Map.of(AirbyteIntegrationLauncher.JOB_TYPE, AirbyteIntegrationLauncher.SYNC_JOB, AirbyteIntegrationLauncher.SYNC_STEP,
            AirbyteIntegrationLauncher.NORMALIZE_STEP),
        Map.of(),
        Map.of(),
        "run",
        "--integration-type", "bigquery",
        "--config", WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
        "--catalog", WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME))
            .thenReturn(process);
    when(process.getInputStream()).thenReturn(new ByteArrayInputStream("hello".getBytes(StandardCharsets.UTF_8)));
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("hello".getBytes(StandardCharsets.UTF_8)));
  }

  @AfterEach
  public void tearDown() throws IOException {
    // The log file needs to be present and empty
    final Path logFile = logJobRoot.resolve(LogClientSingleton.LOG_FILENAME);
    if (Files.exists(logFile)) {
      Files.delete(logFile);
    }
    Files.createFile(logFile);
  }

  @Test
  void test() throws Exception {
    final NormalizationRunner runner =
        new DefaultNormalizationRunner(workerConfigs, DestinationType.BIGQUERY, processFactory,
            NormalizationRunnerFactory.BASE_NORMALIZATION_IMAGE_NAME);

    when(process.exitValue()).thenReturn(0);

    assertTrue(runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, workerConfigs.getResourceRequirements()));
  }

  @Test
  void testLog() throws Exception {

    final NormalizationRunner runner =
        new DefaultNormalizationRunner(workerConfigs, DestinationType.BIGQUERY, processFactory,
            NormalizationRunnerFactory.BASE_NORMALIZATION_IMAGE_NAME);

    when(process.exitValue()).thenReturn(0);

    assertTrue(runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, workerConfigs.getResourceRequirements()));

    final Path logPath = logJobRoot.resolve(LogClientSingleton.LOG_FILENAME);
    final Stream<String> logs = IOs.readFile(logPath).lines();

    logs
        .filter(line -> !line.contains("EnvConfigs(getEnvOrDefault)"))
        .forEach(line -> {
          org.assertj.core.api.Assertions.assertThat(line)
              .startsWith(Color.GREEN_BACKGROUND.getCode() + "normalization" + RESET);
        });
  }

  @Test
  public void testClose() throws Exception {
    when(process.isAlive()).thenReturn(true).thenReturn(false);

    final NormalizationRunner runner =
        new DefaultNormalizationRunner(workerConfigs, DestinationType.BIGQUERY, processFactory,
            NormalizationRunnerFactory.BASE_NORMALIZATION_IMAGE_NAME);
    runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, workerConfigs.getResourceRequirements());
    runner.close();

    verify(process).waitFor();
  }

  @Test
  public void testFailure() {
    doThrow(new RuntimeException()).when(process).exitValue();

    final NormalizationRunner runner =
        new DefaultNormalizationRunner(workerConfigs, DestinationType.BIGQUERY, processFactory,
            NormalizationRunnerFactory.BASE_NORMALIZATION_IMAGE_NAME);
    assertThrows(RuntimeException.class,
        () -> runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, workerConfigs.getResourceRequirements()));

    verify(process).destroy();
  }

}
