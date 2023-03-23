/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import com.fasterxml.jackson.annotation.JsonValue;
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
  private static final String CONNECTOR_COMMAND_METADATA_KEY = "connector_command";

  public enum ConnectorCommand {

    SPEC("spec"),
    CHECK("check"),
    DISCOVER("discover"),
    WRITE("write"),
    READ("read");

    private final String value;

    ConnectorCommand(final String value) {
      this.value = value;
    }

    @Override
    @JsonValue
    public String toString() {
      return String.valueOf(value);
    }

  }

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

  public static FailureReason connectorCommandFailure(final AirbyteTraceMessage m,
                                                      final Long jobId,
                                                      final Integer attemptNumber,
                                                      final ConnectorCommand connectorCommand) {
    final Metadata metadata = traceMessageMetadata(jobId, attemptNumber);
    metadata.withAdditionalProperty(CONNECTOR_COMMAND_METADATA_KEY, connectorCommand.toString());
    return genericFailure(m, jobId, attemptNumber)
        .withMetadata(metadata);
  }

  public static FailureReason connectorCommandFailure(final Throwable t,
                                                      final Long jobId,
                                                      final Integer attemptNumber,
                                                      final ConnectorCommand connectorCommand) {
    final Metadata metadata = jobAndAttemptMetadata(jobId, attemptNumber);
    metadata.withAdditionalProperty(CONNECTOR_COMMAND_METADATA_KEY, connectorCommand.toString());
    return genericFailure(t, jobId, attemptNumber)
        .withMetadata(metadata);
  }

  public static FailureReason sourceFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return connectorCommandFailure(t, jobId, attemptNumber, ConnectorCommand.READ)
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withExternalMessage("Something went wrong within the source connector");
  }

  public static FailureReason sourceFailure(final AirbyteTraceMessage m, final Long jobId, final Integer attemptNumber) {
    return connectorCommandFailure(m, jobId, attemptNumber, ConnectorCommand.READ)
        .withFailureOrigin(FailureOrigin.SOURCE);
  }

  public static FailureReason destinationFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return connectorCommandFailure(t, jobId, attemptNumber, ConnectorCommand.WRITE)
        .withFailureOrigin(FailureOrigin.DESTINATION)
        .withExternalMessage("Something went wrong within the destination connector");
  }

  public static FailureReason destinationFailure(final AirbyteTraceMessage m, final Long jobId, final Integer attemptNumber) {
    return connectorCommandFailure(m, jobId, attemptNumber, ConnectorCommand.WRITE)
        .withFailureOrigin(FailureOrigin.DESTINATION);
  }

  public static FailureReason checkFailure(final Throwable t,
                                           final Long jobId,
                                           final Integer attemptNumber,
                                           final FailureReason.FailureOrigin origin) {
    return connectorCommandFailure(t, jobId, attemptNumber, ConnectorCommand.CHECK)
        .withFailureOrigin(origin)
        .withFailureType(FailureReason.FailureType.CONFIG_ERROR)
        .withRetryable(false)
        .withExternalMessage(String
            .format("Checking %s connection failed - please review this connection's configuration to prevent future syncs from failing", origin));
  }

  public static FailureReason unknownOriginFailure(final Throwable t, final Long jobId, final Integer attemptNumber) {
    return genericFailure(t, jobId, attemptNumber)
        .withFailureOrigin(FailureOrigin.UNKNOWN)
        .withExternalMessage("An unknown failure occurred");
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
