/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.Configs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.TolerationPOJO;
import java.util.List;
import java.util.Map;

public class WorkerConfigs {

  private final Configs.WorkerEnvironment workerEnvironment;
  private final ResourceRequirements resourceRequirements;
  private final List<TolerationPOJO> workerPodTolerations;
  private final Map<String, String> workerPodNodeSelectors;
  private final String jobImagePullSecret;
  private final String jobImagePullPolicy;
  private final String jobSocatImage;
  private final String jobBusyboxImage;
  private final String jobCurlImage;

  public WorkerConfigs(final Configs configs) {
    this.workerEnvironment = configs.getWorkerEnvironment();
    this.resourceRequirements = new ResourceRequirements()
        .withCpuRequest(configs.getJobMainContainerCpuRequest())
        .withCpuLimit(configs.getJobMainContainerCpuLimit())
        .withMemoryRequest(configs.getJobMainContainerMemoryRequest())
        .withMemoryLimit(configs.getJobMainContainerMemoryLimit());
    this.workerPodTolerations = configs.getJobKubeTolerations();
    this.workerPodNodeSelectors = configs.getJobKubeNodeSelectors();
    this.jobImagePullSecret = configs.getJobKubeMainContainerImagePullSecret();
    this.jobImagePullPolicy = configs.getJobKubeMainContainerImagePullPolicy();
    this.jobSocatImage = configs.getJobKubeSocatImage();
    this.jobBusyboxImage = configs.getJobKubeBusyboxImage();
    this.jobCurlImage = configs.getJobKubeCurlImage();
  }

  public Configs.WorkerEnvironment getWorkerEnvironment() {
    return workerEnvironment;
  }

  public ResourceRequirements getResourceRequirements() {
    return resourceRequirements;
  }

  public List<TolerationPOJO> getWorkerPodTolerations() {
    return workerPodTolerations;
  }

  public Map<String, String> getWorkerPodNodeSelectors() {
    return workerPodNodeSelectors;
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

}
