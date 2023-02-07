/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import static io.airbyte.workers.process.Metadata.CHECK_JOB;
import static io.airbyte.workers.process.Metadata.DISCOVER_JOB;
import static io.airbyte.workers.process.Metadata.JOB_TYPE_KEY;
import static io.airbyte.workers.process.Metadata.READ_STEP;
import static io.airbyte.workers.process.Metadata.SPEC_JOB;
import static io.airbyte.workers.process.Metadata.SYNC_JOB;
import static io.airbyte.workers.process.Metadata.SYNC_STEP_KEY;
import static io.airbyte.workers.process.Metadata.WRITE_STEP;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.WorkerEnvConstants;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class AirbyteIntegrationLauncherTest {

  private static final String CONFIG = "config";
  private static final String CATALOG = "catalog";
  private static final String CONFIG_ARG = "--config";
  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;
  private static final Path JOB_ROOT = Path.of("abc");
  public static final String FAKE_IMAGE = "fake_image";
  private static final Map<String, String> CONFIG_FILES = ImmutableMap.of(
      CONFIG, "{}");
  private static final Map<String, String> CONFIG_CATALOG_FILES = ImmutableMap.of(
      CONFIG, "{}",
      CATALOG, "{}");
  private static final Map<String, String> CONFIG_CATALOG_STATE_FILES = ImmutableMap.of(
      CONFIG, "{}",
      CATALOG, "{}",
      "state", "{}");

  private static final FeatureFlags FEATURE_FLAGS = new EnvVariableFeatureFlags();
  private static final Configs CONFIGS = new EnvConfigs();

  private static final Map<String, String> JOB_METADATA = Map.of(
      WorkerEnvConstants.WORKER_CONNECTOR_IMAGE, FAKE_IMAGE,
      WorkerEnvConstants.WORKER_JOB_ID, JOB_ID,
      WorkerEnvConstants.WORKER_JOB_ATTEMPT, String.valueOf(JOB_ATTEMPT),
      EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, String.valueOf(FEATURE_FLAGS.useStreamCapableState()),
      EnvVariableFeatureFlags.AUTO_DETECT_SCHEMA, String.valueOf(FEATURE_FLAGS.autoDetectSchema()),
      EnvVariableFeatureFlags.APPLY_FIELD_SELECTION, String.valueOf(FEATURE_FLAGS.applyFieldSelection()),
      EnvVariableFeatureFlags.FIELD_SELECTION_WORKSPACES, FEATURE_FLAGS.fieldSelectionWorkspaces(),
      EnvConfigs.SOCAT_KUBE_CPU_REQUEST, CONFIGS.getSocatSidecarKubeCpuRequest(),
      EnvConfigs.SOCAT_KUBE_CPU_LIMIT, CONFIGS.getSocatSidecarKubeCpuLimit(),
      EnvConfigs.LAUNCHDARKLY_KEY, CONFIGS.getLaunchDarklyKey());

  private WorkerConfigs workerConfigs;
  @Mock
  private ProcessFactory processFactory;
  private AirbyteIntegrationLauncher launcher;

  @BeforeEach
  void setUp() {
    workerConfigs = new WorkerConfigs(new EnvConfigs());
    launcher = new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, FAKE_IMAGE, processFactory, workerConfigs.getResourceRequirements(), null, false,
        FEATURE_FLAGS);
  }

  @Test
  void spec() throws WorkerException {
    launcher.spec(JOB_ROOT);

    Mockito.verify(processFactory).create(SPEC_JOB, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, false, Collections.emptyMap(), null,
        workerConfigs.getResourceRequirements(), null, Map.of(JOB_TYPE_KEY, SPEC_JOB), JOB_METADATA,
        Map.of(),
        "spec");
  }

  @Test
  void check() throws WorkerException {
    launcher.check(JOB_ROOT, CONFIG, "{}");

    Mockito.verify(processFactory).create(CHECK_JOB, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, false, CONFIG_FILES, null,
        workerConfigs.getResourceRequirements(),
        null,
        Map.of(JOB_TYPE_KEY, CHECK_JOB),
        JOB_METADATA,
        Map.of(),
        "check",
        CONFIG_ARG, CONFIG);
  }

  @Test
  void discover() throws WorkerException {
    launcher.discover(JOB_ROOT, CONFIG, "{}");

    Mockito.verify(processFactory).create(DISCOVER_JOB, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, false, CONFIG_FILES, null,
        workerConfigs.getResourceRequirements(),
        null,
        Map.of(JOB_TYPE_KEY, DISCOVER_JOB),
        JOB_METADATA,
        Map.of(),
        "discover",
        CONFIG_ARG, CONFIG);
  }

  @Test
  void read() throws WorkerException {
    launcher.read(JOB_ROOT, CONFIG, "{}", CATALOG, "{}", "state", "{}");

    Mockito.verify(processFactory).create(READ_STEP, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, false, CONFIG_CATALOG_STATE_FILES, null,
        workerConfigs.getResourceRequirements(),
        null,
        Map.of(JOB_TYPE_KEY, SYNC_JOB, SYNC_STEP_KEY, READ_STEP),
        JOB_METADATA,
        Map.of(),
        Lists.newArrayList(
            "read",
            CONFIG_ARG, CONFIG,
            "--catalog", CATALOG,
            "--state", "state").toArray(new String[0]));
  }

  @Test
  void write() throws WorkerException {
    launcher.write(JOB_ROOT, CONFIG, "{}", CATALOG, "{}");

    Mockito.verify(processFactory).create(WRITE_STEP, JOB_ID, JOB_ATTEMPT, JOB_ROOT, FAKE_IMAGE, false, true, CONFIG_CATALOG_FILES, null,
        workerConfigs.getResourceRequirements(),
        null,
        Map.of(JOB_TYPE_KEY, SYNC_JOB, SYNC_STEP_KEY, WRITE_STEP),
        JOB_METADATA,
        Map.of(),
        "write",
        CONFIG_ARG, CONFIG,
        "--catalog", CATALOG);
  }

}
