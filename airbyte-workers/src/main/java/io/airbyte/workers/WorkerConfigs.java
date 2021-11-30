/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.Configs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.WorkerPodToleration;
import java.util.List;
import java.util.Map;

public class WorkerConfigs {

  private final Configs.WorkerEnvironment workerEnvironment;
  private final ResourceRequirements resourceRequirements;
  private final List<WorkerPodToleration> workerPodTolerations;
  private final Map<String, String> workerPodNodeSelectors;
  private final String jobImagePullSecret;
  private final String jobImagePullPolicy;
  private final String jobSocatImage;
  private final String jobBusyboxImage;
  private final String jobCurlImage;

  public WorkerConfigs(final Configs configs) {
    this.workerEnvironment = configs.getWorkerEnvironment();
    this.resourceRequirements = new ResourceRequirements()
        .withCpuRequest(configs.getCpuRequest())
        .withCpuLimit(configs.getCpuLimit())
        .withMemoryRequest(configs.getMemoryRequest())
        .withMemoryLimit(configs.getMemoryLimit());
    this.workerPodTolerations = configs.getWorkerPodTolerations();
    this.workerPodNodeSelectors = configs.getWorkerNodeSelectors();
    this.jobImagePullSecret = configs.getJobsImagePullSecret();
    this.jobImagePullPolicy = configs.getJobImagePullPolicy();
    this.jobSocatImage = configs.getJobSocatImage();
    this.jobBusyboxImage = configs.getJobBusyboxImage();
    this.jobCurlImage = configs.getJobCurlImage();
  }

  public Configs.WorkerEnvironment getWorkerEnvironment() {
    return workerEnvironment;
  }

  public ResourceRequirements getResourceRequirements() {
    return resourceRequirements;
  }

  public List<WorkerPodToleration> getWorkerPodTolerations() {
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
