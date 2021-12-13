/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.workers.temporal.exception.NonRetryableException;
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

  @ActivityMethod
  AttemptCreationOutput createNewAttempt(AttemptCreationInput input) throws NonRetryableException;

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobSuccessInput {

    private long jobId;
    private int attemptId;

  }

  @ActivityMethod
  void jobSuccess(JobSuccessInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobFailureInput {

    private long jobId;

  }

  @ActivityMethod
  void jobFailure(JobFailureInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class AttemptFailureInput {

    private long jobId;
    private int attemptId;

  }

  @ActivityMethod
  void attemptFailure(AttemptFailureInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobCancelledInput {

    private long jobId;

  }

  @ActivityMethod
  void jobCancelled(JobCancelledInput input);

}
