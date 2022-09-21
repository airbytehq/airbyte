/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.models.AttemptNormalizationStatus;
import java.io.IOException;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
public class NormalizationSummaryCheckActivityImpl implements NormalizationSummaryCheckActivity {

  private final Optional<JobPersistence> jobPersistence;

  public NormalizationSummaryCheckActivityImpl(final Optional<JobPersistence> jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  @Override
  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  public boolean shouldRunNormalization(final Long jobId, final Long attemptNumber, final Optional<Long> numCommittedRecords) throws IOException {
    // if job persistence is unavailable, default to running normalization
    if (jobPersistence.isEmpty()) {
      return true;
    }

    // if the count of committed records for this attempt is > 0 OR if it is null,
    // then we should run normalization
    if (numCommittedRecords.get() == null || numCommittedRecords.get() > 0) {
      return true;
    }

    final List<AttemptNormalizationStatus> attemptNormalizationStatuses = jobPersistence.get().getAttemptNormalizationStatusesForJob(jobId);
    final AtomicLong totalRecordsCommitted = new AtomicLong(0L);
    final AtomicBoolean shouldReturnTrue = new AtomicBoolean(false);

    attemptNormalizationStatuses.stream().sorted(Comparator.comparing(AttemptNormalizationStatus::getAttemptNumber).reversed()).toList()
        .forEach(n -> {
          if (n.getAttemptNumber() == attemptNumber) {
            return;
          }

          // if normalization succeeded from a previous attempt succeeded,
          // we can stop looking for previous attempts
          if (!n.getNormalizationFailed()) {
            return;
          }

          // if normalization failed on past attempt, add number of records committed on that attempt to total
          // committed number
          // if there is no data recorded for the number of committed records, we should assume that there
          // were committed records and run normalization
          if (n.getRecordsCommitted().isEmpty()) {
            shouldReturnTrue.set(true);
            return;
          } else if (n.getRecordsCommitted().get() != 0L) {
            totalRecordsCommitted.set(totalRecordsCommitted.get() + n.getRecordsCommitted().get());
          }
        });

    if (shouldReturnTrue.get() || totalRecordsCommitted.get() > 0L) {
      return true;
    }

    return false;

  }

}
