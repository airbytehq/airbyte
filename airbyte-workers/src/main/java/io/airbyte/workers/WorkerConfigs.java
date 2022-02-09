/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.Configs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.TolerationPOJO;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class WorkerConfigs {

  private static final Duration DEFAULT_WORKER_STATUS_CHECK_INTERVAL = Duration.ofSeconds(30);
  private static final Duration SPEC_WORKER_STATUS_CHECK_INTERVAL = Duration.ofSeconds(1);
  private static final Duration CHECK_WORKER_STATUS_CHECK_INTERVAL = Duration.ofSeconds(1);
  private static final Duration DISCOVER_WORKER_STATUS_CHECK_INTERVAL = Duration.ofSeconds(1);
  private static final Duration SYNC_WORKER_STATUS_CHECK_INTERVAL = Duration.ofSeconds(30);

  private final Configs.WorkerEnvironment workerEnvironment;

  // for running source, destination, normalization, dbt, normalization orchestrator, and dbt
  // orchestrator pods
  private final ResourceRequirements resourceRequirements;
  // for running replication orchestrator pods
  private final ResourceRequirements replicationOrchestratorResourceRequirements;

  private final List<TolerationPOJO> workerKubeTolerations;
  private final Optional<Map<String, String>> workerKubeNodeSelectors;
  private final String jobImagePullSecret;
  private final String jobImagePullPolicy;
  private final String jobSocatImage;
  private final String jobBusyboxImage;
  private final String jobCurlImage;
  private final Map<String, String> envMap;
  private final Duration workerStatusCheckInterval;


  /**
   * Constructs a job-type-agnostic WorkerConfigs. For WorkerConfigs customized for specific
   * job-types, use static `build*JOBTYPE*WorkerConfigs` method if one exists.
   */
  public WorkerConfigs(final Configs configs) {
    this(
        configs.getWorkerEnvironment(),
        new ResourceRequirements()
            .withCpuRequest(configs.getJobMainContainerCpuRequest())
            .withCpuLimit(configs.getJobMainContainerCpuLimit())
            .withMemoryRequest(configs.getJobMainContainerMemoryRequest())
            .withMemoryLimit(configs.getJobMainContainerMemoryLimit()),
        new ResourceRequirements()
            .withCpuRequest(configs.getReplicationOrchestratorCpuRequest())
            .withCpuLimit(configs.getReplicationOrchestratorCpuLimit())
            .withMemoryRequest(configs.getReplicationOrchestratorMemoryRequest())
            .withMemoryLimit(configs.getReplicationOrchestratorMemoryLimit()),
        configs.getJobKubeTolerations(),
        configs.getJobKubeNodeSelectors(),
        configs.getJobKubeMainContainerImagePullSecret(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap(),
        DEFAULT_WORKER_STATUS_CHECK_INTERVAL);
  }

  /**
   * Builds a WorkerConfigs with some configs that are specific to the Spec job type.
   */
  public static WorkerConfigs buildSpecWorkerConfigs(final Configs configs) {
    final Optional<Map<String, String>> nodeSelectors = configs.getSpecJobKubeNodeSelectors().isPresent()
        ? configs.getSpecJobKubeNodeSelectors()
        : configs.getJobKubeNodeSelectors();

    return new WorkerConfigs(
        configs.getWorkerEnvironment(),
        new ResourceRequirements()
            .withCpuRequest(configs.getJobMainContainerCpuRequest())
            .withCpuLimit(configs.getJobMainContainerCpuLimit())
            .withMemoryRequest(configs.getJobMainContainerMemoryRequest())
            .withMemoryLimit(configs.getJobMainContainerMemoryLimit()),
        new ResourceRequirements()
            .withCpuRequest(configs.getReplicationOrchestratorCpuRequest())
            .withCpuLimit(configs.getReplicationOrchestratorCpuLimit())
            .withMemoryRequest(configs.getReplicationOrchestratorMemoryRequest())
            .withMemoryLimit(configs.getReplicationOrchestratorMemoryLimit()),
        configs.getJobKubeTolerations(),
        nodeSelectors,
        configs.getJobKubeMainContainerImagePullSecret(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap(),
        SPEC_WORKER_STATUS_CHECK_INTERVAL);
  }

  /**
   * Builds a WorkerConfigs with some configs that are specific to the Check job type.
   */
  public static WorkerConfigs buildCheckWorkerConfigs(final Configs configs) {
    final Optional<Map<String, String>> nodeSelectors = configs.getCheckJobKubeNodeSelectors().isPresent()
        ? configs.getCheckJobKubeNodeSelectors()
        : configs.getJobKubeNodeSelectors();

    return new WorkerConfigs(
        configs.getWorkerEnvironment(),
        new ResourceRequirements()
            .withCpuRequest(configs.getJobMainContainerCpuRequest())
            .withCpuLimit(configs.getJobMainContainerCpuLimit())
            .withMemoryRequest(configs.getJobMainContainerMemoryRequest())
            .withMemoryLimit(configs.getJobMainContainerMemoryLimit()),
        new ResourceRequirements()
            .withCpuRequest(configs.getReplicationOrchestratorCpuRequest())
            .withCpuLimit(configs.getReplicationOrchestratorCpuLimit())
            .withMemoryRequest(configs.getReplicationOrchestratorMemoryRequest())
            .withMemoryLimit(configs.getReplicationOrchestratorMemoryLimit()),
        configs.getJobKubeTolerations(),
        nodeSelectors,
        configs.getJobKubeMainContainerImagePullSecret(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap(),
        CHECK_WORKER_STATUS_CHECK_INTERVAL);
  }

  /**
   * Builds a WorkerConfigs with some configs that are specific to the Discover job type.
   */
  public static WorkerConfigs buildDiscoverWorkerConfigs(final Configs configs) {
    final Optional<Map<String, String>> nodeSelectors = configs.getDiscoverJobKubeNodeSelectors().isPresent()
        ? configs.getDiscoverJobKubeNodeSelectors()
        : configs.getJobKubeNodeSelectors();

    return new WorkerConfigs(
        configs.getWorkerEnvironment(),
        new ResourceRequirements()
            .withCpuRequest(configs.getJobMainContainerCpuRequest())
            .withCpuLimit(configs.getJobMainContainerCpuLimit())
            .withMemoryRequest(configs.getJobMainContainerMemoryRequest())
            .withMemoryLimit(configs.getJobMainContainerMemoryLimit()),
        new ResourceRequirements()
            .withCpuRequest(configs.getReplicationOrchestratorCpuRequest())
            .withCpuLimit(configs.getReplicationOrchestratorCpuLimit())
            .withMemoryRequest(configs.getReplicationOrchestratorMemoryRequest())
            .withMemoryLimit(configs.getReplicationOrchestratorMemoryLimit()),
        configs.getJobKubeTolerations(),
        nodeSelectors,
        configs.getJobKubeMainContainerImagePullSecret(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap(),
        DISCOVER_WORKER_STATUS_CHECK_INTERVAL);
  }

  /**
   * Builds a WorkerConfigs with some configs that are specific to the Sync job type.
   */
  public static WorkerConfigs buildSyncWorkerConfigs(final Configs configs) {
    final Optional<Map<String, String>> nodeSelectors = configs.getSyncJobKubeNodeSelectors().isPresent()
        ? configs.getSyncJobKubeNodeSelectors()
        : configs.getJobKubeNodeSelectors();

    return new WorkerConfigs(
        configs.getWorkerEnvironment(),
        new ResourceRequirements()
            .withCpuRequest(configs.getJobMainContainerCpuRequest())
            .withCpuLimit(configs.getJobMainContainerCpuLimit())
            .withMemoryRequest(configs.getJobMainContainerMemoryRequest())
            .withMemoryLimit(configs.getJobMainContainerMemoryLimit()),
        new ResourceRequirements()
            .withCpuRequest(configs.getReplicationOrchestratorCpuRequest())
            .withCpuLimit(configs.getReplicationOrchestratorCpuLimit())
            .withMemoryRequest(configs.getReplicationOrchestratorMemoryRequest())
            .withMemoryLimit(configs.getReplicationOrchestratorMemoryLimit()),
        configs.getJobKubeTolerations(),
        nodeSelectors,
        configs.getJobKubeMainContainerImagePullSecret(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap(),
        SYNC_WORKER_STATUS_CHECK_INTERVAL);
  }

  public Configs.WorkerEnvironment getWorkerEnvironment() {
    return workerEnvironment;
  }

  public ResourceRequirements getResourceRequirements() {
    return resourceRequirements;
  }

  public List<TolerationPOJO> getWorkerKubeTolerations() {
    return workerKubeTolerations;
  }

  public Optional<Map<String, String>> getworkerKubeNodeSelectors() {
    return workerKubeNodeSelectors;
  }

  public String getJobImagePullSecret() {
    return jobImagePullSecret;
  }

  public String getJobImagePullPolicy() {
    return jobImagePullPolicy;
  }

  public String getJobSocatImage() {
    return jobSocatImage;
  }

  public String getJobBusyboxImage() {
    return jobBusyboxImage;
  }

  public String getJobCurlImage() {
    return jobCurlImage;
  }

  public Map<String, String> getEnvMap() {
    return envMap;
  }

  public ResourceRequirements getReplicationOrchestratorResourceRequirements() {
    return replicationOrchestratorResourceRequirements;
  }

  public Duration getWorkerStatusCheckInterval() {
    return workerStatusCheckInterval;
  }

}
