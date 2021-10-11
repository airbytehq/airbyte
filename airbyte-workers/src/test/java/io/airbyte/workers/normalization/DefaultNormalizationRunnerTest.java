/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.normalization.DefaultNormalizationRunner.DestinationType;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultNormalizationRunnerTest {

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;

  private Path jobRoot;
  private ProcessFactory processFactory;
  private Process process;
  private JsonNode config;
  private ConfiguredAirbyteCatalog catalog;

  @BeforeEach
  void setup() throws IOException, WorkerException {
    jobRoot = Files.createDirectories(Files.createTempDirectory("test"));
    processFactory = mock(ProcessFactory.class);
    process = mock(Process.class);

    config = mock(JsonNode.class);
    catalog = mock(ConfiguredAirbyteCatalog.class);

    final Map<String, String> files = ImmutableMap.of(
        WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME, Jsons.serialize(config),
        WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME, Jsons.serialize(catalog));

    when(processFactory.create(JOB_ID, JOB_ATTEMPT, jobRoot, DefaultNormalizationRunner.NORMALIZATION_IMAGE_NAME, false, files, null,
        WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS,
        Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_JOB, KubeProcessFactory.SYNC_STEP, KubeProcessFactory.NORMALISE_STEP),
        "run",
        "--integration-type", "bigquery",
        "--config", WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
        "--catalog", WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME))
            .thenReturn(process);
    when(process.getInputStream()).thenReturn(new ByteArrayInputStream("hello".getBytes()));
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("hello".getBytes()));
  }

  @Test
  void test() throws Exception {
    final NormalizationRunner runner = new DefaultNormalizationRunner(DestinationType.BIGQUERY, processFactory);

    when(process.exitValue()).thenReturn(0);

    assertTrue(runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS));
  }

  @Test
  public void testClose() throws Exception {
    when(process.isAlive()).thenReturn(true).thenReturn(false);

    final NormalizationRunner runner = new DefaultNormalizationRunner(DestinationType.BIGQUERY, processFactory);
    runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);
    runner.close();

    verify(process).waitFor();
  }

  @Test
  public void testFailure() {
    doThrow(new RuntimeException()).when(process).exitValue();

    final NormalizationRunner runner = new DefaultNormalizationRunner(DestinationType.BIGQUERY, processFactory);
    assertThrows(RuntimeException.class,
        () -> runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS));

    verify(process).destroy();
  }

}
