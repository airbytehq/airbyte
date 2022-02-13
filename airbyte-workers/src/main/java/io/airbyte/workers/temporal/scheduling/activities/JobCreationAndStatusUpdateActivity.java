/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.workers.temporal.exception.RetryableException;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface JobCreationAndStatusUpdateActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobCreationInput {

    private UUID connectionId;
    private boolean reset;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobCreationOutput {

    private long jobId;

  }

  /**
   * Creates a new job
   *
   * @param input - POJO that contains the connections
   * @return a POJO that contains the jobId
   */
  @ActivityMethod
  JobCreationOutput createNewJob(JobCreationInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class AttemptCreationInput {

    private long jobId;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class AttemptCreationOutput {

    private int attemptId;

  }

  /**
   * Create a new attempt for a given job ID
   *
   * @param input POJO containing the jobId
   * @return A POJO containing the attemptId
   */
  @ActivityMethod
  AttemptCreationOutput createNewAttempt(AttemptCreationInput input) throws RetryableException;

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobSuccessInput {

    private long jobId;
    private int attemptId;
    private StandardSyncOutput standardSyncOutput;

  }

  /**
   * Set a job status as successful
   */
  @ActivityMethod
  void jobSuccess(JobSuccessInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobFailureInput {

    private long jobId;
    private String reason;

  }

  /**
   * Set a job status as failed
   */
  @ActivityMethod
  void jobFailure(JobFailureInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class AttemptFailureInput {

    private long jobId;
    private int attemptId;
    private StandardSyncOutput standardSyncOutput;
    private AttemptFailureSummary attemptFailureSummary;

  }

  /**
   * Set an attempt status as failed
   */
  @ActivityMethod
  void attemptFailure(AttemptFailureInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobCancelledInput {

    private long jobId;
    private int attemptId;
    private AttemptFailureSummary attemptFailureSummary;

  }

  /**
   * Set a job status as cancelled
   */
  @ActivityMethod
  void jobCancelled(JobCancelledInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class ReportJobStartInput {

    private long jobId;

  }

  @ActivityMethod
  void reportJobStart(ReportJobStartInput reportJobStartInput);

}
