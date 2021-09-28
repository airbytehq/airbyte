/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteIntegrationLauncher implements IntegrationLauncher {

  private final static Logger LOGGER = LoggerFactory.getLogger(AirbyteIntegrationLauncher.class);

  private final String jobId;
  private final int attempt;
  private final String imageName;
  private final ProcessFactory processFactory;
  private final ResourceRequirements resourceRequirement;

  public AirbyteIntegrationLauncher(String jobId,
                                    int attempt,
                                    final String imageName,
                                    final ProcessFactory processFactory) {
    this(String.valueOf(jobId), attempt, imageName, processFactory, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);
  }

  public AirbyteIntegrationLauncher(String jobId,
                                    int attempt,
                                    final String imageName,
                                    final ProcessFactory processFactory,
                                    final ResourceRequirements resourceRequirement) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.imageName = imageName;
    this.processFactory = processFactory;
    this.resourceRequirement = resourceRequirement;
  }

  @Override
  public Process spec(final Path jobRoot) throws WorkerException {
    return processFactory.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        false,
        Collections.emptyMap(),
        null,
        resourceRequirement,
        Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SPEC_JOB),
        "spec");
  }

  @Override
  public Process check(final Path jobRoot, final String configFilename, final String configContents) throws WorkerException {
    return processFactory.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        false,
        ImmutableMap.of(configFilename, configContents),
        null,
        resourceRequirement,
        Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.CHECK_JOB),
        "check",
        "--config", configFilename);
  }

  @Override
  public Process discover(final Path jobRoot, final String configFilename, final String configContents) throws WorkerException {
    return processFactory.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        false,
        ImmutableMap.of(configFilename, configContents),
        null,
        resourceRequirement,
        Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.DISCOVER_JOB),
        "discover",
        "--config", configFilename);
  }

  @Override
  public Process read(final Path jobRoot,
                      final String configFilename,
                      final String configContents,
                      final String catalogFilename,
                      final String catalogContents,
                      final String stateFilename,
                      final String stateContents)
      throws WorkerException {
    final List<String> arguments = Lists.newArrayList(
        "read",
        "--config", configFilename,
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
        jobId,
        attempt,
        jobRoot,
        imageName,
        false,
        files,
        null,
        resourceRequirement,
        Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_JOB, KubeProcessFactory.SYNC_STEP, KubeProcessFactory.READ_STEP),
        arguments);
  }

  @Override
  public Process write(final Path jobRoot,
                       final String configFilename,
                       final String configContents,
                       final String catalogFilename,
                       final String catalogContents)
      throws WorkerException {
    final Map<String, String> files = ImmutableMap.of(
        configFilename, configContents,
        catalogFilename, catalogContents);

    return processFactory.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        true,
        files,
        null,
        resourceRequirement,
        Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_JOB, KubeProcessFactory.SYNC_STEP, KubeProcessFactory.WRITE_STEP),
        "write",
        "--config", configFilename,
        "--catalog", catalogFilename);
  }

}
