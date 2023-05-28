/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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

import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.configoss.AllowedHosts;
import io.airbyte.configoss.ResourceRequirements;
import io.airbyte.workers.exception.TestHarnessException;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class AirbyteIntegrationLauncher implements IntegrationLauncher {

  private static final String CONFIG = "--config";

  private final String jobId;
  private final int attempt;
  private final String imageName;
  private final ProcessFactory processFactory;
  private final ResourceRequirements resourceRequirement;
  private final FeatureFlags featureFlags;

  /**
   * If true, launcher will use a separated isolated pool to run the job.
   * <p>
   * At this moment, we put custom connector jobs into an isolated pool.
   */
  private final boolean useIsolatedPool;
  private final AllowedHosts allowedHosts;

  public AirbyteIntegrationLauncher(final String jobId,
                                    final int attempt,
                                    final String imageName,
                                    final ProcessFactory processFactory,
                                    final ResourceRequirements resourceRequirement,
                                    final AllowedHosts allowedHosts,
                                    final boolean useIsolatedPool,
                                    final FeatureFlags featureFlags) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.imageName = imageName;
    this.processFactory = processFactory;
    this.resourceRequirement = resourceRequirement;
    this.allowedHosts = allowedHosts;
    this.featureFlags = featureFlags;
    this.useIsolatedPool = useIsolatedPool;
  }

  @Override
  public Process spec(final Path jobRoot) throws TestHarnessException {
    return processFactory.create(
        SPEC_JOB,
        jobId,
        attempt,
        jobRoot,
        imageName,
        useIsolatedPool,
        false,
        Collections.emptyMap(),
        null,
        resourceRequirement,
        allowedHosts,
        Map.of(JOB_TYPE_KEY, SPEC_JOB),
        getWorkerMetadata(),
        Collections.emptyMap(),
        Collections.emptyMap(),
        "spec");
  }

  @Override
  public Process check(final Path jobRoot, final String configFilename, final String configContents) throws TestHarnessException {
    return processFactory.create(
        CHECK_JOB,
        jobId,
        attempt,
        jobRoot,
        imageName,
        useIsolatedPool,
        false,
        ImmutableMap.of(configFilename, configContents),
        null,
        resourceRequirement,
        allowedHosts,
        Map.of(JOB_TYPE_KEY, CHECK_JOB),
        getWorkerMetadata(),
        Collections.emptyMap(),
        Collections.emptyMap(),
        "check",
        CONFIG, configFilename);
  }

  @Override
  public Process discover(final Path jobRoot, final String configFilename, final String configContents) throws TestHarnessException {
    return processFactory.create(
        DISCOVER_JOB,
        jobId,
        attempt,
        jobRoot,
        imageName,
        useIsolatedPool,
        false,
        ImmutableMap.of(configFilename, configContents),
        null,
        resourceRequirement,
        allowedHosts,
        Map.of(JOB_TYPE_KEY, DISCOVER_JOB),
        getWorkerMetadata(),
        Collections.emptyMap(),
        Collections.emptyMap(),
        "discover",
        CONFIG, configFilename);
  }

  @Override
  public Process read(final Path jobRoot,
                      final String configFilename,
                      final String configContents,
                      final String catalogFilename,
                      final String catalogContents,
                      final String stateFilename,
                      final String stateContents)
      throws TestHarnessException {
    final List<String> arguments = Lists.newArrayList(
        "read",
        CONFIG, configFilename,
        "--catalog", catalogFilename);

    final Map<String, String> files = new HashMap<>();
    files.put(configFilename, configContents);
    files.put(catalogFilename, catalogContents);

    if (stateFilename != null) {
      arguments.add("--state");
      arguments.add(stateFilename);

      Preconditions.checkNotNull(stateContents);
      files.put(stateFilename, stateContents);
    }

    return processFactory.create(
        READ_STEP,
        jobId,
        attempt,
        jobRoot,
        imageName,
        useIsolatedPool,
        false,
        files,
        null,
        resourceRequirement,
        allowedHosts,
        Map.of(JOB_TYPE_KEY, SYNC_JOB, SYNC_STEP_KEY, READ_STEP),
        getWorkerMetadata(),
        Collections.emptyMap(),
        Collections.emptyMap(),
        arguments.toArray(new String[arguments.size()]));
  }

  @Override
  public Process write(final Path jobRoot,
                       final String configFilename,
                       final String configContents,
                       final String catalogFilename,
                       final String catalogContents,
                       final Map<String, String> additionalEnvironmentVariables)
      throws TestHarnessException {
    final Map<String, String> files = ImmutableMap.of(
        configFilename, configContents,
        catalogFilename, catalogContents);

    return processFactory.create(
        WRITE_STEP,
        jobId,
        attempt,
        jobRoot,
        imageName,
        useIsolatedPool,
        true,
        files,
        null,
        resourceRequirement,
        allowedHosts,
        Map.of(JOB_TYPE_KEY, SYNC_JOB, SYNC_STEP_KEY, WRITE_STEP),
        getWorkerMetadata(),
        Collections.emptyMap(),
        additionalEnvironmentVariables,
        "write",
        CONFIG, configFilename,
        "--catalog", catalogFilename);
  }

  private Map<String, String> getWorkerMetadata() {
    // We've managed to exceed the maximum number of parameters for Map.of(), so use a builder + convert
    // back to hashmap
    return Maps.newHashMap(
        ImmutableMap.<String, String>builder()
            .put("WORKER_CONNECTOR_IMAGE", imageName)
            .put("WORKER_JOB_ID", jobId)
            .put("WORKER_JOB_ATTEMPT", String.valueOf(attempt))
            .put(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, String.valueOf(featureFlags.useStreamCapableState()))
            .put(EnvVariableFeatureFlags.AUTO_DETECT_SCHEMA, String.valueOf(featureFlags.autoDetectSchema()))
            .put(EnvVariableFeatureFlags.APPLY_FIELD_SELECTION, String.valueOf(featureFlags.applyFieldSelection()))
            .put(EnvVariableFeatureFlags.FIELD_SELECTION_WORKSPACES, featureFlags.fieldSelectionWorkspaces())
            .build());
  }

}
