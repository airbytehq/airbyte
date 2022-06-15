/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import static io.airbyte.workers.process.AirbyteIntegrationLauncher.*;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.WorkerEnvConstants;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class AirbyteIntegrationLauncherTest {

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;
  private static final Path JOB_ROOT = Path.of("abc");
  public static final String FAKE_IMAGE = "fake_image";
  private static final Map<String, String> CONFIG_FILES = ImmutableMap.of(
      "config", "{}");
  private static final Map<String, String> CONFIG_CATALOG_FILES = ImmutableMap.of(
      "config", "{}",
      "catalog", "{}");
  private static final Map<String, String> CONFIG_CATALOG_STATE_FILES = ImmutableMap.of(
      "config", "{}",
      "catalog", "{}",
      "state", "{}");
  private static final Map<String, String> JOB_METADATA = Map.of(
      WorkerEnvConstants.WORKER_CONNECTOR_IMAGE, FAKE_IMAGE,
      WorkerEnvConstants.WORKER_JOB_ID, JOB_ID,
      WorkerEnvConstants.WORKER_JOB_ATTEMPT, String.valueOf(JOB_ATTEMPT));

  private WorkerConfigs workerConfigs;
  private ProcessFactory processFactory;
  private AirbyteIntegrationLauncher launcher;

  @BeforeEach
  void setUp() {
    workerConfigs = new WorkerConfigs(new EnvConfigs());
    processFactory = Mockito.mock(ProcessFactory.class);
    launcher = new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, FAKE_IMAGE, processFactory, workerConfigs.getResourceRequirements());
  }

  @Test
  void spec() throws WorkerException {
    launcher.spec(JOB_ROOT);

    Mockito.verify(processFactory).create(SPEC_JOB, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, Collections.emptyMap(), null,
        workerConfigs.getResourceRequirements(), Map.of(AirbyteIntegrationLauncher.JOB_TYPE, AirbyteIntegrationLauncher.SPEC_JOB), JOB_METADATA,
        Map.of(),
        "spec");
  }

  @Test
  void check() throws WorkerException {
    launcher.check(JOB_ROOT, "config", "{}");

    Mockito.verify(processFactory).create(CHECK_JOB, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, CONFIG_FILES, null,
        workerConfigs.getResourceRequirements(),
        Map.of(JOB_TYPE, CHECK_JOB),
        JOB_METADATA,
        Map.of(),
        "check",
        "--config", "config");
  }

  @Test
  void discover() throws WorkerException {
    launcher.discover(JOB_ROOT, "config", "{}");

    Mockito.verify(processFactory).create(DISCOVER_JOB, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, CONFIG_FILES, null,
        workerConfigs.getResourceRequirements(),
        Map.of(JOB_TYPE, DISCOVER_JOB),
        JOB_METADATA,
        Map.of(),
        "discover",
        "--config", "config");
  }

  @Test
  void read() throws WorkerException {
    launcher.read(JOB_ROOT, "config", "{}", "catalog", "{}", "state", "{}");

    Mockito.verify(processFactory).create(READ_STEP, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, CONFIG_CATALOG_STATE_FILES, null,
        workerConfigs.getResourceRequirements(),
        Map.of(JOB_TYPE, SYNC_JOB, SYNC_STEP, READ_STEP),
        JOB_METADATA,
        Map.of(),
        Lists.newArrayList(
            "read",
            "--config", "config",
            "--catalog", "catalog",
            "--state", "state").toArray(new String[0]));
  }

  @Test
  void write() throws WorkerException {
    launcher.write(JOB_ROOT, "config", "{}", "catalog", "{}");

    Mockito.verify(processFactory).create(WRITE_STEP, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, true, CONFIG_CATALOG_FILES, null,
        workerConfigs.getResourceRequirements(),
        Map.of(JOB_TYPE, SYNC_JOB, SYNC_STEP, WRITE_STEP),
        JOB_METADATA,
        Map.of(),
        "write",
        "--config", "config",
        "--catalog", "catalog");
  }

}
