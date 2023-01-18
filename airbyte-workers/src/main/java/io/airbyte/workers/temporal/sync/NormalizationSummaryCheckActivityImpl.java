/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.ATTEMPT_NUMBER_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;

import datadog.trace.api.Trace;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.model.generated.AttemptNormalizationStatusRead;
import io.airbyte.api.client.model.generated.AttemptNormalizationStatusReadList;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.temporal.activity.Activity;
import jakarta.inject.Singleton;
import java.util.Comparator;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
public class NormalizationSummaryCheckActivityImpl implements NormalizationSummaryCheckActivity {

  private final AirbyteApiClient airbyteApiClient;

  public NormalizationSummaryCheckActivityImpl(final AirbyteApiClient airbyteApiClient) {
    this.airbyteApiClient = airbyteApiClient;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  public boolean shouldRunNormalization(final Long jobId, final Long attemptNumber, final Optional<Long> numCommittedRecords) {
    ApmTraceUtils.addTagsToTrace(Map.of(ATTEMPT_NUMBER_KEY, attemptNumber, JOB_ID_KEY, jobId));

    // if the count of committed records for this attempt is > 0 OR if it is null,
    // then we should run normalization
    if (numCommittedRecords.isEmpty() || numCommittedRecords.get() > 0) {
      return true;
    }

    final AttemptNormalizationStatusReadList AttemptNormalizationStatusReadList;
    try {
      AttemptNormalizationStatusReadList = AirbyteApiClient.retryWithJitter(
          () -> airbyteApiClient.getJobsApi().getAttemptNormalizationStatusesForJob(new JobIdRequestBody().id(jobId)),
          "get normalization statuses");
    } catch (final Exception e) {
      throw Activity.wrap(e);
    }
    final AtomicLong totalRecordsCommitted = new AtomicLong(0L);
    final AtomicBoolean shouldReturnTrue = new AtomicBoolean(false);

    AttemptNormalizationStatusReadList.getAttemptNormalizationStatuses().stream().sorted(Comparator.comparing(
        AttemptNormalizationStatusRead::getAttemptNumber).reversed()).toList()
        .forEach(n -> {
          // Have to cast it because attemptNumber is read from JobRunConfig.
          if (n.getAttemptNumber().intValue() == attemptNumber) {
            return;
          }

          // if normalization succeeded from a previous attempt succeeded,
          // we can stop looking for previous attempts
          if (!n.getHasNormalizationFailed()) {
            return;
          }

          // if normalization failed on past attempt, add number of records committed on that attempt to total
          // committed number
          // if there is no data recorded for the number of committed records, we should assume that there
          // were committed records and run normalization
          if (!n.getHasRecordsCommitted()) {
            shouldReturnTrue.set(true);
            return;
          } else if (n.getRecordsCommitted().longValue() != 0L) {
            totalRecordsCommitted.addAndGet(n.getRecordsCommitted());
          }
        });

    if (shouldReturnTrue.get() || totalRecordsCommitted.get() > 0L) {
      return true;
    }

    return false;

  }

}
