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
import java.util.concurrent.atomic.AtomicReference;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Singleton
@AllArgsConstructor
@NoArgsConstructor
@Slf4j
public class NormalizationSummaryCheckActivityImpl implements NormalizationSummaryCheckActivity {

  @Inject
  private JobPersistence jobPersistence;

  @Override
  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  public Boolean shouldRunNormalization(final Long jobId, final Long attemptNumber, final Optional<Long> numCommittedRecords) throws IOException {
    // if the count of committed records for this attempt is > 0 OR if it is null,
    // then we should run normalization
    if (numCommittedRecords.get() == null || numCommittedRecords.get() > 0) {
      return true;
    }

    final List<AttemptNormalizationStatus> attemptNormalizationStatuses = jobPersistence.getAttemptNormalizationStatusesForJob(jobId);
    final AtomicReference<Long> totalRecordsCommitted = new AtomicReference<>(0L);
    final AtomicReference<Boolean> shouldReturnTrue = new AtomicReference<>(false);

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

          // if normalization failed on past attempt,
          // add number of records committed on that attempt to
          // total committed number
          if (n.getNormalizationFailed()) {
            // if there is no data recorded for the number of committed records, we should assume that there
            // were committed records and run normalization
            if (n.getRecordsCommitted().get() == null) {
              shouldReturnTrue.set(true);
              return;
            } else if (n.getRecordsCommitted().get() != 0L) {
              totalRecordsCommitted.set(totalRecordsCommitted.get() + n.getRecordsCommitted().get());
            }
          }
        });

    if (shouldReturnTrue.get() || totalRecordsCommitted.get() > 0L) {
      return true;
    }

    return false;

  }

}
