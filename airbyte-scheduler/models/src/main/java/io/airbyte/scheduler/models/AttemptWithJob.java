/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.models;

public class AttemptWithJob {

  private final Attempt attempt;
  private final Job job;

  public Job getJob() {
    return job;
  }

  public Attempt getAttempt() {
    return attempt;
  }

  public AttemptWithJob(final Attempt attempt, final Job job) {
    this.attempt = attempt;
    this.job = job;
  }

}
