/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs.migrations;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Metadata;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_35_40_001__MigrateFailureReasonEnumValues extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_40_001__MigrateFailureReasonEnumValues.class);
  private static final String NULL = "<null>";

  @VisibleForTesting
  static String OLD_MANUAL_CANCELLATION = "manualCancellation";
  static String NEW_MANUAL_CANCELLATION = "manual_cancellation";
  static String OLD_SYSTEM_ERROR = "systemError";
  static String NEW_SYSTEM_ERROR = "system_error";
  static String OLD_CONFIG_ERROR = "configError";
  static String NEW_CONFIG_ERROR = "config_error";
  static String OLD_REPLICATION_ORIGIN = "replicationWorker";
  static String NEW_REPLICATION_ORIGIN = "replication";
  static String OLD_UNKNOWN = "unknown";

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    updateRecordsWithNewEnumValues(ctx);
  }

  /**
   * Finds all attempt record that have a failure summary containing a deprecated enum value. For each
   * record, calls method to fix and update.
   */
  static void updateRecordsWithNewEnumValues(final DSLContext ctx) {
    final Result<Record> results =
        ctx.fetch(String.format("""
                                SELECT A.* FROM attempts A, jsonb_array_elements(A.failure_summary->'failures') as f
                                WHERE f->>'failureOrigin' = '%s'
                                OR f->>'failureOrigin' = '%s'
                                OR f->>'failureType' = '%s'
                                OR f->>'failureType' = '%s'
                                OR f->>'failureType' = '%s'
                                OR f->>'failureType' = '%s'
                                """, OLD_UNKNOWN, OLD_REPLICATION_ORIGIN, OLD_UNKNOWN, OLD_CONFIG_ERROR, OLD_SYSTEM_ERROR, OLD_MANUAL_CANCELLATION));
    results.forEach(record -> updateAttemptFailureReasons(ctx, record));
  }

  /**
   * Takes in a single record from the above query and performs an UPDATE to set the failure summary
   * to the fixed version.
   */
  private static void updateAttemptFailureReasons(final DSLContext ctx, final Record record) {
    final Field<Long> attemptIdField = DSL.field("id", SQLDataType.BIGINT);
    final Field<JSONB> failureSummaryField = DSL.field("failure_summary", SQLDataType.JSONB.nullable(true));

    final Long attemptId = record.get(attemptIdField);
    final AttemptFailureSummaryForMigration oldFailureSummary = Jsons.deserialize(
        record.get(failureSummaryField).data(),
        AttemptFailureSummaryForMigration.class);

    final AttemptFailureSummaryForMigration fixedFailureSummary = getFixedAttemptFailureSummary(oldFailureSummary);

    ctx.update(DSL.table("attempts"))
        .set(failureSummaryField, JSONB.valueOf(Jsons.serialize(fixedFailureSummary)))
        .where(attemptIdField.eq(attemptId))
        .execute();
  }

  /**
   * Takes in a FailureSummary and replaces deprecated enum values with their updated versions.
   */
  private static AttemptFailureSummaryForMigration getFixedAttemptFailureSummary(final AttemptFailureSummaryForMigration failureSummary) {
    final Map<String, String> oldFailureTypeToFixedFailureType = ImmutableMap.of(
        OLD_MANUAL_CANCELLATION, NEW_MANUAL_CANCELLATION,
        OLD_SYSTEM_ERROR, NEW_SYSTEM_ERROR,
        OLD_CONFIG_ERROR, NEW_CONFIG_ERROR);

    final Map<String, String> oldFailureOriginToFixedFailureOrigin = ImmutableMap.of(
        OLD_REPLICATION_ORIGIN, NEW_REPLICATION_ORIGIN);

    final List<FailureReasonForMigration> fixedFailureReasons = new ArrayList<>();

    failureSummary.getFailures().stream().forEach(failureReason -> {
      final String failureType = failureReason.getFailureType();
      final String failureOrigin = failureReason.getFailureOrigin();

      // null failureType is valid and doesn't need correction
      if (failureType != null) {
        if (oldFailureTypeToFixedFailureType.containsKey(failureType)) {
          failureReason.setFailureType(oldFailureTypeToFixedFailureType.get(failureType));
        } else if (failureType.equals(OLD_UNKNOWN)) {
          failureReason.setFailureType(null);
        }
      }

      // null failureOrigin is valid and doesn't need correction
      if (failureOrigin != null) {
        if (oldFailureOriginToFixedFailureOrigin.containsKey(failureOrigin)) {
          failureReason.setFailureOrigin(oldFailureOriginToFixedFailureOrigin.get(failureOrigin));
        } else if (failureOrigin.equals(OLD_UNKNOWN)) {
          failureReason.setFailureOrigin(null);
        }
      }

      fixedFailureReasons.add(failureReason);
    });

    failureSummary.setFailures(fixedFailureReasons);
    return failureSummary;
  }

  /**
   * The following classes are essentially a copy of the FailureReason and AttemptFailureSummary
   * classes at the time of this migration. They support both deprecated and new enum values and are
   * used for record deserialization in this migration because in the future, the real FailureReason
   * class will have those deprecated enum values removed, which would break deserialization within
   * this migration.
   */

  static class FailureReasonForMigration implements Serializable {

    private String failureOrigin;
    private String failureType;
    private String internalMessage;
    private String externalMessage;
    private Metadata metadata;
    private String stacktrace;
    private Boolean retryable;
    private Long timestamp;
    private final static long serialVersionUID = -1485119682657564218L;

    public String getFailureOrigin() {
      return failureOrigin;
    }

    public void setFailureOrigin(final String failureOrigin) {
      this.failureOrigin = failureOrigin;
    }

    public FailureReasonForMigration withFailureOrigin(final String failureOrigin) {
      this.failureOrigin = failureOrigin;
      return this;
    }

    public String getFailureType() {
      return failureType;
    }

    public void setFailureType(final String failureType) {
      this.failureType = failureType;
    }

    public FailureReasonForMigration withFailureType(final String failureType) {
      this.failureType = failureType;
      return this;
    }

    public String getInternalMessage() {
      return internalMessage;
    }

    public void setInternalMessage(final String internalMessage) {
      this.internalMessage = internalMessage;
    }

    public FailureReasonForMigration withInternalMessage(final String internalMessage) {
      this.internalMessage = internalMessage;
      return this;
    }

    public String getExternalMessage() {
      return externalMessage;
    }

    public void setExternalMessage(final String externalMessage) {
      this.externalMessage = externalMessage;
    }

    public FailureReasonForMigration withExternalMessage(final String externalMessage) {
      this.externalMessage = externalMessage;
      return this;
    }

    public Metadata getMetadata() {
      return metadata;
    }

    public void setMetadata(final Metadata metadata) {
      this.metadata = metadata;
    }

    public FailureReasonForMigration withMetadata(final Metadata metadata) {
      this.metadata = metadata;
      return this;
    }

    public String getStacktrace() {
      return stacktrace;
    }

    public void setStacktrace(final String stacktrace) {
      this.stacktrace = stacktrace;
    }

    public FailureReasonForMigration withStacktrace(final String stacktrace) {
      this.stacktrace = stacktrace;
      return this;
    }

    public Boolean getRetryable() {
      return retryable;
    }

    public void setRetryable(final Boolean retryable) {
      this.retryable = retryable;
    }

    public FailureReasonForMigration withRetryable(final Boolean retryable) {
      this.retryable = retryable;
      return this;
    }

    public Long getTimestamp() {
      return timestamp;
    }

    public void setTimestamp(final Long timestamp) {
      this.timestamp = timestamp;
    }

    public FailureReasonForMigration withTimestamp(final Long timestamp) {
      this.timestamp = timestamp;
      return this;
    }

    @Override
    public String toString() {
      final StringBuilder sb = new StringBuilder();
      sb.append(FailureReasonForMigration.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
      sb.append("failureOrigin");
      sb.append('=');
      sb.append(((this.failureOrigin == null) ? NULL : this.failureOrigin));
      sb.append(',');
      sb.append("failureType");
      sb.append('=');
      sb.append(((this.failureType == null) ? NULL : this.failureType));
      sb.append(',');
      sb.append("internalMessage");
      sb.append('=');
      sb.append(((this.internalMessage == null) ? NULL : this.internalMessage));
      sb.append(',');
      sb.append("externalMessage");
      sb.append('=');
      sb.append(((this.externalMessage == null) ? NULL : this.externalMessage));
      sb.append(',');
      sb.append("metadata");
      sb.append('=');
      sb.append(((this.metadata == null) ? NULL : this.metadata));
      sb.append(',');
      sb.append("stacktrace");
      sb.append('=');
      sb.append(((this.stacktrace == null) ? NULL : this.stacktrace));
      sb.append(',');
      sb.append("retryable");
      sb.append('=');
      sb.append(((this.retryable == null) ? NULL : this.retryable));
      sb.append(',');
      sb.append("timestamp");
      sb.append('=');
      sb.append(((this.timestamp == null) ? NULL : this.timestamp));
      sb.append(',');
      if (sb.charAt((sb.length() - 1)) == ',') {
        sb.setCharAt((sb.length() - 1), ']');
      } else {
        sb.append(']');
      }
      return sb.toString();
    }

    @Override
    public int hashCode() {
      int result = 1;
      result = ((result * 31) + ((this.retryable == null) ? 0 : this.retryable.hashCode()));
      result = ((result * 31) + ((this.metadata == null) ? 0 : this.metadata.hashCode()));
      result = ((result * 31) + ((this.stacktrace == null) ? 0 : this.stacktrace.hashCode()));
      result = ((result * 31) + ((this.failureOrigin == null) ? 0 : this.failureOrigin.hashCode()));
      result = ((result * 31) + ((this.failureType == null) ? 0 : this.failureType.hashCode()));
      result = ((result * 31) + ((this.internalMessage == null) ? 0 : this.internalMessage.hashCode()));
      result = ((result * 31) + ((this.externalMessage == null) ? 0 : this.externalMessage.hashCode()));
      result = ((result * 31) + ((this.timestamp == null) ? 0 : this.timestamp.hashCode()));
      return result;
    }

    @Override
    public boolean equals(final Object other) {
      if (other == this) {
        return true;
      }
      if ((other instanceof FailureReasonForMigration) == false) {
        return false;
      }
      final FailureReasonForMigration rhs = ((FailureReasonForMigration) other);
      return (((((((((this.retryable == rhs.retryable) || ((this.retryable != null) && this.retryable.equals(rhs.retryable)))
          && ((this.metadata == rhs.metadata) || ((this.metadata != null) && this.metadata.equals(rhs.metadata))))
          && ((this.stacktrace == rhs.stacktrace) || ((this.stacktrace != null) && this.stacktrace.equals(rhs.stacktrace))))
          && ((this.failureOrigin == rhs.failureOrigin) || ((this.failureOrigin != null) && this.failureOrigin.equals(rhs.failureOrigin))))
          && ((this.failureType == rhs.failureType) || ((this.failureType != null) && this.failureType.equals(rhs.failureType))))
          && ((this.internalMessage == rhs.internalMessage) || ((this.internalMessage != null) && this.internalMessage.equals(rhs.internalMessage))))
          && ((this.externalMessage == rhs.externalMessage) || ((this.externalMessage != null) && this.externalMessage.equals(rhs.externalMessage))))
          && ((this.timestamp == rhs.timestamp) || ((this.timestamp != null) && this.timestamp.equals(rhs.timestamp))));
    }

  }

  static class AttemptFailureSummaryForMigration implements Serializable {

    private List<FailureReasonForMigration> failures = new ArrayList<>();
    private Boolean partialSuccess;
    private final static long serialVersionUID = -9065693637249217586L;

    public List<FailureReasonForMigration> getFailures() {
      return failures;
    }

    public void setFailures(final List<FailureReasonForMigration> failures) {
      this.failures = failures;
    }

    public AttemptFailureSummaryForMigration withFailures(final List<FailureReasonForMigration> failures) {
      this.failures = failures;
      return this;
    }

    public Boolean getPartialSuccess() {
      return partialSuccess;
    }

    public void setPartialSuccess(final Boolean partialSuccess) {
      this.partialSuccess = partialSuccess;
    }

    public AttemptFailureSummaryForMigration withPartialSuccess(final Boolean partialSuccess) {
      this.partialSuccess = partialSuccess;
      return this;
    }

    @Override
    public String toString() {
      final StringBuilder sb = new StringBuilder();
      sb.append(AttemptFailureSummaryForMigration.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
      sb.append("failures");
      sb.append('=');
      sb.append(((this.failures == null) ? NULL : this.failures));
      sb.append(',');
      sb.append("partialSuccess");
      sb.append('=');
      sb.append(((this.partialSuccess == null) ? NULL : this.partialSuccess));
      sb.append(',');
      if (sb.charAt((sb.length() - 1)) == ',') {
        sb.setCharAt((sb.length() - 1), ']');
      } else {
        sb.append(']');
      }
      return sb.toString();
    }

    @Override
    public int hashCode() {
      int result = 1;
      result = ((result * 31) + ((this.partialSuccess == null) ? 0 : this.partialSuccess.hashCode()));
      result = ((result * 31) + ((this.failures == null) ? 0 : this.failures.hashCode()));
      return result;
    }

    @Override
    public boolean equals(final Object other) {
      if (other == this) {
        return true;
      }
      if ((other instanceof AttemptFailureSummaryForMigration) == false) {
        return false;
      }
      final AttemptFailureSummaryForMigration rhs = ((AttemptFailureSummaryForMigration) other);
      return (((this.partialSuccess == rhs.partialSuccess) || ((this.partialSuccess != null) && this.partialSuccess.equals(rhs.partialSuccess)))
          && ((this.failures == rhs.failures) || ((this.failures != null) && this.failures.equals(rhs.failures))));
    }

  }

}
