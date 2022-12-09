/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.Configs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.TolerationPOJO;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class WorkerConfigs {

  private final Configs.WorkerEnvironment workerEnvironment;
  private final ResourceRequirements resourceRequirements;
  private final List<TolerationPOJO> workerKubeTolerations;
  private final Map<String, String> workerKubeNodeSelectors;
  private final Optional<Map<String, String>> workerIsolatedKubeNodeSelectors;
  private final Map<String, String> workerKubeAnnotations;
  private final List<String> jobImagePullSecrets;
  private final String jobImagePullPolicy;
  private final String sidecarImagePullPolicy;
  private final String jobSocatImage;
  private final String jobBusyboxImage;
  private final String jobCurlImage;
  private final Map<String, String> envMap;

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
        configs.getJobKubeTolerations(),
        configs.getJobKubeNodeSelectors(),
        configs.getUseCustomKubeNodeSelector() ? Optional.of(configs.getIsolatedJobKubeNodeSelectors()) : Optional.empty(),
        configs.getJobKubeAnnotations(),
        configs.getJobKubeMainContainerImagePullSecrets(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSidecarContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap());
  }

  /**
   * Builds a WorkerConfigs with some configs that are specific to the Spec job type.
   */
  public static WorkerConfigs buildSpecWorkerConfigs(final Configs configs) {
    final Map<String, String> nodeSelectors = configs.getSpecJobKubeNodeSelectors() != null
        ? configs.getSpecJobKubeNodeSelectors()
        : configs.getJobKubeNodeSelectors();

    final Map<String, String> annotations = configs.getSpecJobKubeAnnotations() != null
        ? configs.getSpecJobKubeAnnotations()
        : configs.getJobKubeAnnotations();

    return new WorkerConfigs(
        configs.getWorkerEnvironment(),
        new ResourceRequirements()
            .withCpuRequest(configs.getJobMainContainerCpuRequest())
            .withCpuLimit(configs.getJobMainContainerCpuLimit())
            .withMemoryRequest(configs.getJobMainContainerMemoryRequest())
            .withMemoryLimit(configs.getJobMainContainerMemoryLimit()),
        configs.getJobKubeTolerations(),
        nodeSelectors,
        configs.getUseCustomKubeNodeSelector() ? Optional.of(configs.getIsolatedJobKubeNodeSelectors()) : Optional.empty(),
        annotations,
        configs.getJobKubeMainContainerImagePullSecrets(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSidecarContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap());
  }

  /**
   * Builds a WorkerConfigs with some configs that are specific to the Check job type.
   */
  public static WorkerConfigs buildCheckWorkerConfigs(final Configs configs) {
    final Map<String, String> nodeSelectors = configs.getCheckJobKubeNodeSelectors() != null
        ? configs.getCheckJobKubeNodeSelectors()
        : configs.getJobKubeNodeSelectors();

    final Map<String, String> annotations = configs.getCheckJobKubeAnnotations() != null
        ? configs.getCheckJobKubeAnnotations()
        : configs.getJobKubeAnnotations();

    return new WorkerConfigs(
        configs.getWorkerEnvironment(),
        new ResourceRequirements()
            .withCpuRequest(configs.getCheckJobMainContainerCpuRequest())
            .withCpuLimit(configs.getCheckJobMainContainerCpuLimit())
            .withMemoryRequest(configs.getCheckJobMainContainerMemoryRequest())
            .withMemoryLimit(configs.getCheckJobMainContainerMemoryLimit()),
        configs.getJobKubeTolerations(),
        nodeSelectors,
        configs.getUseCustomKubeNodeSelector() ? Optional.of(configs.getIsolatedJobKubeNodeSelectors()) : Optional.empty(),
        annotations,
        configs.getJobKubeMainContainerImagePullSecrets(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSidecarContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap());
  }

  /**
   * Builds a WorkerConfigs with some configs that are specific to the Discover job type.
   */
  public static WorkerConfigs buildDiscoverWorkerConfigs(final Configs configs) {
    final Map<String, String> nodeSelectors = configs.getDiscoverJobKubeNodeSelectors() != null
        ? configs.getDiscoverJobKubeNodeSelectors()
        : configs.getJobKubeNodeSelectors();

    final Map<String, String> annotations = configs.getDiscoverJobKubeAnnotations() != null
        ? configs.getDiscoverJobKubeAnnotations()
        : configs.getJobKubeAnnotations();

    return new WorkerConfigs(
        configs.getWorkerEnvironment(),
        new ResourceRequirements()
            .withCpuRequest(configs.getJobMainContainerCpuRequest())
            .withCpuLimit(configs.getJobMainContainerCpuLimit())
            .withMemoryRequest(configs.getJobMainContainerMemoryRequest())
            .withMemoryLimit(configs.getJobMainContainerMemoryLimit()),
        configs.getJobKubeTolerations(),
        nodeSelectors,
        configs.getUseCustomKubeNodeSelector() ? Optional.of(configs.getIsolatedJobKubeNodeSelectors()) : Optional.empty(),
        annotations,
        configs.getJobKubeMainContainerImagePullSecrets(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSidecarContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap());
  }

  public static WorkerConfigs buildReplicationWorkerConfigs(final Configs configs) {
    return new WorkerConfigs(
        configs.getWorkerEnvironment(),
        new ResourceRequirements()
            .withCpuRequest(configs.getReplicationOrchestratorCpuRequest())
            .withCpuLimit(configs.getReplicationOrchestratorCpuLimit())
            .withMemoryRequest(configs.getReplicationOrchestratorMemoryRequest())
            .withMemoryLimit(configs.getReplicationOrchestratorMemoryLimit()),
        configs.getJobKubeTolerations(),
        configs.getJobKubeNodeSelectors(),
        configs.getUseCustomKubeNodeSelector() ? Optional.of(configs.getIsolatedJobKubeNodeSelectors()) : Optional.empty(),
        configs.getJobKubeAnnotations(),
        configs.getJobKubeMainContainerImagePullSecrets(),
        configs.getJobKubeMainContainerImagePullPolicy(),
        configs.getJobKubeSidecarContainerImagePullPolicy(),
        configs.getJobKubeSocatImage(),
        configs.getJobKubeBusyboxImage(),
        configs.getJobKubeCurlImage(),
        configs.getJobDefaultEnvMap());
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

  public Map<String, String> getworkerKubeNodeSelectors() {
    return workerKubeNodeSelectors;
  }

  public Optional<Map<String, String>> getWorkerIsolatedKubeNodeSelectors() {
    return workerIsolatedKubeNodeSelectors;
  }

  public Map<String, String> getWorkerKubeAnnotations() {
    return workerKubeAnnotations;
  }

  public List<String> getJobImagePullSecrets() {
    return jobImagePullSecrets;
  }

  public String getJobImagePullPolicy() {
    return jobImagePullPolicy;
  }

  public String getSidecarImagePullPolicy() {
    return sidecarImagePullPolicy;
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

}
