/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.JobsApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.AttemptNormalizationStatusRead;
import io.airbyte.api.client.model.generated.AttemptNormalizationStatusReadList;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.workers.temporal.sync.NormalizationSummaryCheckActivityImpl;
import java.util.List;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;

@Slf4j
@ExtendWith(MockitoExtension.class)
class NormalizationSummaryCheckActivityTest {

  private static final Long JOB_ID = 10L;
  static private NormalizationSummaryCheckActivityImpl normalizationSummaryCheckActivity;
  static private AirbyteApiClient airbyteApiClient;
  static private JobsApi jobsApi;

  @BeforeAll
  static void setUp() {
    airbyteApiClient = mock(AirbyteApiClient.class);
    jobsApi = mock(JobsApi.class);
    when(airbyteApiClient.getJobsApi()).thenReturn(jobsApi);
    normalizationSummaryCheckActivity = new NormalizationSummaryCheckActivityImpl(airbyteApiClient);
  }

  @Test
  void testShouldRunNormalizationRecordsCommittedOnFirstAttemptButNotCurrentAttempt() throws ApiException {
    // Attempt 1 committed records, but normalization failed
    // Attempt 2 did not commit records, normalization failed (or did not run)
    final AttemptNormalizationStatusRead attempt1 =
        new AttemptNormalizationStatusRead().attemptNumber(1).hasRecordsCommitted(true).recordsCommitted(10L).hasNormalizationFailed(true);
    final AttemptNormalizationStatusRead attempt2 =
        new AttemptNormalizationStatusRead().attemptNumber(2).hasRecordsCommitted(true).recordsCommitted(0L).hasNormalizationFailed(true);

    when(jobsApi.getAttemptNormalizationStatusesForJob(new JobIdRequestBody().id(JOB_ID)))
        .thenReturn(new AttemptNormalizationStatusReadList().attemptNormalizationStatuses(List.of(attempt1, attempt2)));

    Assertions.assertThat(true).isEqualTo(normalizationSummaryCheckActivity.shouldRunNormalization(JOB_ID, 3L, Optional.of(0L)));
  }

  @Test
  void testShouldRunNormalizationRecordsCommittedOnCurrentAttempt() throws ApiException {
    Assertions.assertThat(true).isEqualTo(normalizationSummaryCheckActivity.shouldRunNormalization(JOB_ID, 3L, Optional.of(30L)));
  }

  @Test
  void testShouldRunNormalizationNoRecordsCommittedOnCurrentAttemptOrPreviousAttempts() throws ApiException {
    // No attempts committed any records
    // Normalization did not run on any attempts
    final AttemptNormalizationStatusRead attempt1 =
        new AttemptNormalizationStatusRead().attemptNumber(1).hasRecordsCommitted(true).recordsCommitted(0L).hasNormalizationFailed(true);
    final AttemptNormalizationStatusRead attempt2 =
        new AttemptNormalizationStatusRead().attemptNumber(2).hasRecordsCommitted(true).recordsCommitted(0L).hasNormalizationFailed(true);

    when(jobsApi.getAttemptNormalizationStatusesForJob(new JobIdRequestBody().id(JOB_ID)))
        .thenReturn(new AttemptNormalizationStatusReadList().attemptNormalizationStatuses(List.of(attempt1, attempt2)));
    Assertions.assertThat(false).isEqualTo(normalizationSummaryCheckActivity.shouldRunNormalization(JOB_ID, 3L, Optional.of(0L)));
  }

  @Test
  void testShouldRunNormalizationNoRecordsCommittedOnCurrentAttemptPreviousAttemptsSucceeded() throws ApiException {
    // Records committed on first two attempts and normalization succeeded
    // No records committed on current attempt and normalization has not yet run
    final AttemptNormalizationStatusRead attempt1 =
        new AttemptNormalizationStatusRead().attemptNumber(1).hasRecordsCommitted(true).recordsCommitted(10L).hasNormalizationFailed(false);
    final AttemptNormalizationStatusRead attempt2 =
        new AttemptNormalizationStatusRead().attemptNumber(2).hasRecordsCommitted(true).recordsCommitted(20L).hasNormalizationFailed(false);

    when(jobsApi.getAttemptNormalizationStatusesForJob(new JobIdRequestBody().id(JOB_ID)))
        .thenReturn(new AttemptNormalizationStatusReadList().attemptNormalizationStatuses(List.of(attempt1, attempt2)));
    Assertions.assertThat(false).isEqualTo(normalizationSummaryCheckActivity.shouldRunNormalization(JOB_ID, 3L, Optional.of(0L)));
  }

}
