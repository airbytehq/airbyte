/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.config.EnvConfigs;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerException;
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

    Mockito.verify(processFactory).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, Collections.emptyMap(), null,
        workerConfigs.getResourceRequirements(), Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SPEC_JOB), Map.of(),
        "spec");
  }

  @Test
  void check() throws WorkerException {
    launcher.check(JOB_ROOT, "config", "{}");

    Mockito.verify(processFactory).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, CONFIG_FILES, null,
        workerConfigs.getResourceRequirements(), Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.CHECK_JOB), Map.of(),
        "check",
        "--config", "config");
  }

  @Test
  void discover() throws WorkerException {
    launcher.discover(JOB_ROOT, "config", "{}");

    Mockito.verify(processFactory).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, CONFIG_FILES, null,
        workerConfigs.getResourceRequirements(), Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.DISCOVER_JOB), Map.of(),
        "discover",
        "--config", "config");
  }

  @Test
  void read() throws WorkerException {
    launcher.read(JOB_ROOT, "config", "{}", "catalog", "{}", "state", "{}");

    Mockito.verify(processFactory).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, CONFIG_CATALOG_STATE_FILES, null,
        workerConfigs.getResourceRequirements(),
        Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_JOB, KubeProcessFactory.SYNC_STEP, KubeProcessFactory.READ_STEP),
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

    Mockito.verify(processFactory).create(JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, true, CONFIG_CATALOG_FILES, null,
        workerConfigs.getResourceRequirements(),
        Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_JOB, KubeProcessFactory.SYNC_STEP, KubeProcessFactory.WRITE_STEP),
        Map.of(),
        "write",
        "--config", "config",
        "--catalog", "catalog");
  }

}
