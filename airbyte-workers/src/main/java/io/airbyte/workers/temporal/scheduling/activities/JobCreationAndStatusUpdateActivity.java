/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.StandardSyncOutput;
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

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobCreationOutput {

    private Long jobId;

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

    private Long jobId;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class AttemptNumberCreationOutput {

    private Integer attemptNumber;

  }

  /**
   * Create a new attempt for a given job ID
   *
   * @param input POJO containing the jobId
   * @return A POJO containing the attemptNumber
   */
  @ActivityMethod
  AttemptNumberCreationOutput createNewAttemptNumber(AttemptCreationInput input) throws RetryableException;

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobSuccessInputWithAttemptNumber {

    private Long jobId;
    private Integer attemptNumber;
    private UUID connectionId;
    private StandardSyncOutput standardSyncOutput;

  }

  /**
   * Set a job status as successful
   */
  @ActivityMethod
  void jobSuccessWithAttemptNumber(JobSuccessInputWithAttemptNumber input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobFailureInput {

    private Long jobId;
    private Integer attemptNumber;
    private UUID connectionId;
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
  class AttemptNumberFailureInput {

    private Long jobId;
    private Integer attemptNumber;
    private UUID connectionId;
    private StandardSyncOutput standardSyncOutput;
    private AttemptFailureSummary attemptFailureSummary;

  }

  /**
   * Set an attempt status as failed
   */
  @ActivityMethod
  void attemptFailureWithAttemptNumber(AttemptNumberFailureInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobCancelledInputWithAttemptNumber {

    private Long jobId;
    private Integer attemptNumber;
    private UUID connectionId;
    private AttemptFailureSummary attemptFailureSummary;

  }

  /**
   * Set a job status as cancelled
   */
  @ActivityMethod
  void jobCancelledWithAttemptNumber(JobCancelledInputWithAttemptNumber input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class ReportJobStartInput {

    private Long jobId;
    private UUID connectionId;

  }

  @ActivityMethod
  void reportJobStart(ReportJobStartInput reportJobStartInput);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class EnsureCleanJobStateInput {

    private UUID connectionId;

  }

  @ActivityMethod
  void ensureCleanJobState(EnsureCleanJobStateInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobCheckFailureInput {

    private Long jobId;
    private Integer attemptId;
    private UUID connectionId;

  }

  @ActivityMethod
  boolean isLastJobOrAttemptFailure(JobCheckFailureInput input);

}
