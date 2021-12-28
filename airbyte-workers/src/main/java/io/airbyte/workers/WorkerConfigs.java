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
  private final List<TolerationPOJO> workerKubeTolerations;
  private final Map<String, String> workerKubeNodeSelectors;
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
    this.workerKubeTolerations = configs.getJobKubeTolerations();
    this.workerKubeNodeSelectors = configs.getJobKubeNodeSelectors();
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

  public List<TolerationPOJO> getWorkerKubeTolerations() {
    return workerKubeTolerations;
  }

  public Map<String, String> getworkerKubeNodeSelectors() {
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

}
