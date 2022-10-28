/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.models;

import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;

public class AttemptWithJobInfo {

  /**
   * This {@link JobInfo} class contains pieces of information about the parent job that may be
   * useful. This approach was taken as opposed to using the actual {@link Job} class here to avoid
   * confusion around the fact that the Job instance would not have its `attempts` field populated.
   */
  public static class JobInfo {

    private final long id;
    private final ConfigType configType;
    private final String scope;
    private final JobConfig config;
    private final JobStatus status;

    public JobInfo(final long id, final ConfigType configType, final String scope, final JobConfig config, final JobStatus status) {
      this.id = id;
      this.configType = configType;
      this.scope = scope;
      this.config = config;
      this.status = status;
    }

    public long getId() {
      return id;
    }

    public ConfigType getConfigType() {
      return configType;
    }

    public String getScope() {
      return scope;
    }

    public JobConfig getConfig() {
      return config;
    }

    public JobStatus getStatus() {
      return status;
    }

  }

  private final Attempt attempt;
  private final JobInfo jobInfo;

  public JobInfo getJobInfo() {
    return jobInfo;
  }

  public Attempt getAttempt() {
    return attempt;
  }

  public AttemptWithJobInfo(final Attempt attempt, final JobInfo jobInfo) {
    this.attempt = attempt;
    this.jobInfo = jobInfo;
  }

  public AttemptWithJobInfo(final Attempt attempt, final Job job) {
    this.attempt = attempt;
    this.jobInfo = new JobInfo(
        job.getId(),
        job.getConfigType(),
        job.getScope(),
        job.getConfig(),
        job.getStatus());
  }

}
