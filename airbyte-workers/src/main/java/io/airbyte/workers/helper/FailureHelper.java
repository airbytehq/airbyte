/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.Metadata;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.util.Comparator;
import java.util.List;
import java.util.Set;
import org.apache.commons.lang3.exception.ExceptionUtils;

public class FailureHelper {

  private static final String JOB_ID_METADATA_KEY = "jobId";
  private static final String ATTEMPT_NUMBER_METADATA_KEY = "attemptNumber";
  private static final String TRACE_MESSAGE_METADATA_KEY = "from_trace_message";

  private static final String WORKFLOW_TYPE_SYNC = "SyncWorkflow";
  private static final String ACTIVITY_TYPE_REPLICATE = "Replicate";
  private static final String ACTIVITY_TYPE_PERSIST = "Persist";
  private static final String ACTIVITY_TYPE_NORMALIZE = "Normalize";
  private static final String ACTIVITY_TYPE_DBT_RUN = "Run";

  public static FailureReason genericFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return new FailureReason()
        .withInternalMessage(t.getMessage())
        .withStacktrace(ExceptionUtils.getStackTrace(t))
        .withTimestamp(System.currentTimeMillis())
        .withMetadata(jobAndAttemptMetadata(jobId, attemptNumber));
  }

  // Generate a FailureReason from an AirbyteTraceMessage.
  // The FailureReason.failureType enum value is taken from the
  // AirbyteErrorTraceMessage.failureType enum value, so the same enum value
  // must exist on both Enums in order to be applied correctly to the FailureReason
  public static FailureReason genericFailure(final AirbyteTraceMessage m, final Long jobId, final Integer attemptNumber) {
    FailureType failureType;
    if (m.getError().getFailureType() == null) {
      // default to system_error when no failure type is set
      failureType = FailureType.SYSTEM_ERROR;
    } else {
      try {
        final String traceMessageError = m.getError().getFailureType().toString();
        failureType = FailureReason.FailureType.fromValue(traceMessageError);
      } catch (final IllegalArgumentException e) {
        // the trace message error does not exist as a FailureReason failure type,
        // so set the failure type to null
        failureType = FailureType.SYSTEM_ERROR;
      }
    }
    return new FailureReason()
        .withInternalMessage(m.getError().getInternalMessage())
        .withExternalMessage(m.getError().getMessage())
        .withStacktrace(m.getError().getStackTrace())
        .withTimestamp(m.getEmittedAt().longValue())
        .withFailureType(failureType)
        .withMetadata(traceMessageMetadata(jobId, attemptNumber));
  }

  public static FailureReason sourceFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return genericFailure(t, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withExternalMessage("Something went wrong within the source connector");
  }

  public static FailureReason sourceFailure(final AirbyteTraceMessage m, final Long jobId, final Integer attemptNumber) {
    return genericFailure(m, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.SOURCE);
  }

  public static FailureReason destinationFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return genericFailure(t, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.DESTINATION)
        .withExternalMessage("Something went wrong within the destination connector");
  }

  public static FailureReason destinationFailure(final AirbyteTraceMessage m, final Long jobId, final Integer attemptNumber) {
    return genericFailure(m, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.DESTINATION);
  }

  public static FailureReason checkFailure(final Throwable t,
                                           final Long jobId,
                                           final Integer attemptNumber,
                                           final FailureReason.FailureOrigin origin) {
    return genericFailure(t, jobId, attemptNumber)
        .withFailureOrigin(origin)
        .withFailureType(FailureReason.FailureType.CONFIG_ERROR)
        .withRetryable(false)
        .withExternalMessage(String
            .format("Checking %s connection failed - please review this connection's configuration to prevent future syncs from failing", origin));
  }

  public static FailureReason replicationFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return genericFailure(t, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.REPLICATION)
        .withExternalMessage("Something went wrong during replication");
  }

  public static FailureReason persistenceFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return genericFailure(t, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.PERSISTENCE)
        .withExternalMessage("Something went wrong during state persistence");
  }

  public static FailureReason normalizationFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return genericFailure(t, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.NORMALIZATION)
        .withExternalMessage("Something went wrong during normalization");
  }

  public static FailureReason normalizationFailure(final AirbyteTraceMessage m, final Long jobId, final Integer attemptNumber) {
    return genericFailure(m, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.NORMALIZATION)
        .withExternalMessage(m.getError().getMessage());
  }

  public static FailureReason dbtFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return genericFailure(t, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.DBT)
        .withExternalMessage("Something went wrong during dbt");
  }

  public static FailureReason unknownOriginFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return genericFailure(t, jobId, attemptNumber)
        .withExternalMessage("An unknown failure occurred");
  }

  public static AttemptFailureSummary failureSummary(final Set<FailureReason> failures, final Boolean partialSuccess) {
    return new AttemptFailureSummary()
        .withFailures(orderedFailures(failures))
        .withPartialSuccess(partialSuccess);
  }

  public static AttemptFailureSummary failureSummaryForCancellation(final Long jobId,
                                                                    final Integer attemptNumber,
                                                                    final Set<FailureReason> failures,
                                                                    final Boolean partialSuccess) {
    failures.add(new FailureReason()
        .withFailureType(FailureType.MANUAL_CANCELLATION)
        .withInternalMessage("Setting attempt to FAILED because the job was cancelled")
        .withExternalMessage("This attempt was cancelled")
        .withTimestamp(System.currentTimeMillis())
        .withMetadata(jobAndAttemptMetadata(jobId, attemptNumber)));

    return failureSummary(failures, partialSuccess);
  }

  public static AttemptFailureSummary failureSummaryForTemporalCleaningJobState(final Long jobId, final Integer attemptNumber) {
    final FailureReason failureReason = new FailureReason()
        .withFailureOrigin(FailureOrigin.AIRBYTE_PLATFORM)
        .withFailureType(FailureType.SYSTEM_ERROR)
        .withInternalMessage(
            "Setting attempt to FAILED because the temporal workflow for this connection was restarted, and existing job state was cleaned.")
        .withExternalMessage("An internal Airbyte error has occurred. This sync will need to be retried.")
        .withTimestamp(System.currentTimeMillis())
        .withMetadata(jobAndAttemptMetadata(jobId, attemptNumber));
    return new AttemptFailureSummary().withFailures(List.of(failureReason));
  }

  public static FailureReason failureReasonFromWorkflowAndActivity(
                                                                   final String workflowType,
                                                                   final String activityType,
                                                                   final Throwable t,
                                                                   final Long jobId,
                                                                   final Integer attemptNumber) {
    if (WORKFLOW_TYPE_SYNC.equals(workflowType) && ACTIVITY_TYPE_REPLICATE.equals(activityType)) {
      return replicationFailure(t, jobId, attemptNumber);
    } else if (WORKFLOW_TYPE_SYNC.equals(workflowType) && ACTIVITY_TYPE_PERSIST.equals(activityType)) {
      return persistenceFailure(t, jobId, attemptNumber);
    } else if (WORKFLOW_TYPE_SYNC.equals(workflowType) && ACTIVITY_TYPE_NORMALIZE.equals(activityType)) {
      return normalizationFailure(t, jobId, attemptNumber);
    } else if (WORKFLOW_TYPE_SYNC.equals(workflowType) && ACTIVITY_TYPE_DBT_RUN.equals(activityType)) {
      return dbtFailure(t, jobId, attemptNumber);
    } else {
      return unknownOriginFailure(t, jobId, attemptNumber);
    }
  }

  private static Metadata jobAndAttemptMetadata(final Long jobId, final Integer attemptNumber) {
    return new Metadata()
        .withAdditionalProperty(JOB_ID_METADATA_KEY, jobId)
        .withAdditionalProperty(ATTEMPT_NUMBER_METADATA_KEY, attemptNumber);
  }

  private static Metadata traceMessageMetadata(final Long jobId, final Integer attemptNumber) {
    return new Metadata()
        .withAdditionalProperty(JOB_ID_METADATA_KEY, jobId)
        .withAdditionalProperty(ATTEMPT_NUMBER_METADATA_KEY, attemptNumber)
        .withAdditionalProperty(TRACE_MESSAGE_METADATA_KEY, true);
  }

  /**
   * Orders failures by putting errors from trace messages first, and then orders by timestamp, so
   * that earlier failures come first.
   */
  public static List<FailureReason> orderedFailures(final Set<FailureReason> failures) {
    final Comparator<FailureReason> compareByIsTrace = Comparator.comparing(failureReason -> {
      final Object metadata = failureReason.getMetadata();
      if (metadata != null) {
        return failureReason.getMetadata().getAdditionalProperties().containsKey(TRACE_MESSAGE_METADATA_KEY) ? 0 : 1;
      } else {
        return 1;
      }
    });
    final Comparator<FailureReason> compareByTimestamp = Comparator.comparing(FailureReason::getTimestamp);
    final Comparator<FailureReason> compareByTraceAndTimestamp = compareByIsTrace.thenComparing(compareByTimestamp);
    return failures.stream().sorted(compareByTraceAndTimestamp).toList();
  }

}
