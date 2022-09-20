/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.models.AttemptNormalizationStatus;
import io.airbyte.workers.temporal.sync.NormalizationSummaryCheckActivityImpl;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class NormalizationSummaryCheckActivityTest {

  private static final Long JOB_ID = 10L;
  @Mock
  private JobPersistence mJobPersistence;

  @InjectMocks
  private NormalizationSummaryCheckActivityImpl normalizationSummaryCheckActivity;

  @Test
  void testShouldRunNormalizationRecordsCommittedOnFirstAttemptButNotCurrentAttempt() throws IOException {
    // Attempt 1 committed records, but normalization failed
    // Attempt 2 did not commit records, normalization failed (or did not run)
    final AttemptNormalizationStatus attempt1 = new AttemptNormalizationStatus(1, Optional.of(10L), true);
    final AttemptNormalizationStatus attempt2 = new AttemptNormalizationStatus(2, Optional.of(0L), true);
    Mockito.when(mJobPersistence.getAttemptNormalizationStatusesForJob(JOB_ID)).thenReturn(List.of(attempt1, attempt2));

    Assertions.assertThat(true).isEqualTo(normalizationSummaryCheckActivity.shouldRunNormalization(JOB_ID, 3L, Optional.of(0L)));
  }

  @Test
  void testShouldRunNormalizationRecordsCommittedOnCurrentAttempt() throws IOException {
    Assertions.assertThat(true).isEqualTo(normalizationSummaryCheckActivity.shouldRunNormalization(JOB_ID, 3L, Optional.of(30L)));
  }

  @Test
  void testShouldRunNormalizationNoRecordsCommittedOnCurrentAttemptOrPreviousAttempts() throws IOException {
    // No attempts committed any records
    // Normalization did not run on any attempts
    final AttemptNormalizationStatus attempt1 = new AttemptNormalizationStatus(1, Optional.of(0L), true);
    final AttemptNormalizationStatus attempt2 = new AttemptNormalizationStatus(2, Optional.of(0L), true);
    Mockito.when(mJobPersistence.getAttemptNormalizationStatusesForJob(JOB_ID)).thenReturn(List.of(attempt1, attempt2));
    Assertions.assertThat(false).isEqualTo(normalizationSummaryCheckActivity.shouldRunNormalization(JOB_ID, 3L, Optional.of(0L)));
  }

  @Test
  void testShouldRunNormalizationNoRecordsCommittedOnCurrentAttemptPreviousAttemptsSucceeded() throws IOException {
    // Records committed on first two attempts and normalization succeeded
    // No records committed on current attempt and normalization has not yet run
    final AttemptNormalizationStatus attempt1 = new AttemptNormalizationStatus(1, Optional.of(10L), false);
    final AttemptNormalizationStatus attempt2 = new AttemptNormalizationStatus(2, Optional.of(20L), false);
    Mockito.when(mJobPersistence.getAttemptNormalizationStatusesForJob(JOB_ID)).thenReturn(List.of(attempt1, attempt2));
    Assertions.assertThat(false).isEqualTo(normalizationSummaryCheckActivity.shouldRunNormalization(JOB_ID, 3L, Optional.of(0L)));
  }

}
