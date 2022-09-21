/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.Mockito.mock;

import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.models.AttemptNormalizationStatus;
import io.airbyte.workers.temporal.sync.NormalizationSummaryCheckActivityImpl;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@Slf4j
@ExtendWith(MockitoExtension.class)
class NormalizationSummaryCheckActivityTest {

  private static final Long JOB_ID = 10L;
  static private NormalizationSummaryCheckActivityImpl normalizationSummaryCheckActivity;
  static private JobPersistence mJobPersistence;

  @BeforeAll
  static void setUp() {
    mJobPersistence = mock(JobPersistence.class);
    normalizationSummaryCheckActivity = new NormalizationSummaryCheckActivityImpl(Optional.of(mJobPersistence));
  }

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
