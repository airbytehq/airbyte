package io.airbyte.db.instance.jobs.migrations;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonValue;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Metadata;
import io.airbyte.db.instance.jobs.migrations.V0_35_40_001__MigrateFailureReasonEnumValues.FailureReasonForMigration.FailureOrigin;
import io.airbyte.db.instance.jobs.migrations.V0_35_40_001__MigrateFailureReasonEnumValues.FailureReasonForMigration.FailureType;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
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

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    updateRecordsWithNewEnumValues(ctx);
  }

  /**
   * Finds all attempt record that have a failure summary containing a deprecated enum value. For each record, calls method to fix and update.
   */
  static void updateRecordsWithNewEnumValues(final DSLContext ctx) {
    final Result<Record> results = ctx.fetch("""
        SELECT A.* FROM attempts A, jsonb_array_elements(A.failure_summary->'failures') as f
        WHERE f->>'failureOrigin' = 'unknown'
        OR f->>'failureOrigin' = 'replicationWorker'
        OR f->>'failureType' = 'unknown'
        OR f->>'failureType' = 'configError'
        OR f->>'failureType' = 'systemError'
        OR f->>'failureType' = 'manualCancellation'
        """);
    results.forEach(record -> updateAttemptFailureReasons(ctx, record));
  }

  /**
   * Takes in a single record from the above query and performs an UPDATE to set the failure summary to the fixed version.
   */
  private static void updateAttemptFailureReasons(final DSLContext ctx, final Record record) {
    final Field<Long> attemptIdField = DSL.field("id", SQLDataType.BIGINT);
    final Field<JSONB> failureSummaryField = DSL.field("failure_summary", SQLDataType.JSONB.nullable(true));

    final Long attemptId = record.get(attemptIdField);
    final AttemptFailureSummaryForMigration oldFailureSummary = Jsons.deserialize(
        record.get(failureSummaryField).data(),
        AttemptFailureSummaryForMigration.class
    );

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
    final Map<FailureType, FailureType> oldFailureTypeToFixedFailureType = ImmutableMap.of(
        FailureType.MANUAL_CANCELLATION_OLD, FailureType.MANUAL_CANCELLATION,
        FailureType.SYSTEM_ERROR_OLD, FailureType.SYSTEM_ERROR,
        FailureType.CONFIG_ERROR_OLD, FailureType.CONFIG_ERROR
    );

    final Map<FailureOrigin, FailureOrigin> oldFailureOriginToFixedFailureOrigin = ImmutableMap.of(
        FailureOrigin.REPLICATION_WORKER, FailureOrigin.REPLICATION
    );

    final List<FailureReasonForMigration> fixedFailureReasons = new ArrayList<>();

    failureSummary.getFailures().stream().forEach(failureReason -> {
      final FailureType failureType = failureReason.getFailureType();
      final FailureOrigin failureOrigin = failureReason.getFailureOrigin();

      // null failureType is valid and doesn't need correction
      if (failureType != null) {
        if (oldFailureTypeToFixedFailureType.containsKey(failureType)) {
          failureReason.setFailureType(oldFailureTypeToFixedFailureType.get(failureType));
        } else if (failureType.equals(FailureType.UNKNOWN)) {
          failureReason.setFailureType(null);
        }
      }

      // null failureOrigin is valid and doesn't need correction
      if (failureOrigin != null) {
        if (oldFailureOriginToFixedFailureOrigin.containsKey(failureOrigin)) {
          failureReason.setFailureOrigin(oldFailureOriginToFixedFailureOrigin.get(failureOrigin));
        } else if (failureOrigin.equals(FailureOrigin.UNKNOWN)) {
          failureReason.setFailureOrigin(null);
        }
      }

      fixedFailureReasons.add(failureReason);
    });

    failureSummary.setFailures(fixedFailureReasons);
    return failureSummary;
  }


  /**
   * The following classes are essentially a copy of the FailureReason and AttemptFailureSummary classes at the time of this migration. They support
   * both deprecated and new enum values and are used for record deserialization in this migration because in the future, the real FailureReason class
   * will have those deprecated enum values removed, which would break deserialization within this migration.
   */

  @JsonInclude(JsonInclude.Include.NON_NULL)
  @JsonPropertyOrder({
      "failureOrigin",
      "failureType",
      "internalMessage",
      "externalMessage",
      "metadata",
      "stacktrace",
      "retryable",
      "timestamp"
  })
  static
  class FailureReasonForMigration {

    @JsonProperty("failureOrigin")
    @JsonPropertyDescription("Indicates where the error originated. If not set, the origin of error is not well known.")
    private FailureReasonForMigration.FailureOrigin failureOrigin;
    @JsonProperty("failureType")
    @JsonPropertyDescription("Categorizes well known errors into types for programmatic handling. If not set, the type of error is not well known.")
    private FailureReasonForMigration.FailureType failureType;
    @JsonProperty("internalMessage")
    @JsonPropertyDescription("Human readable failure description for consumption by technical system operators, like Airbyte engineers or OSS users.")
    private String internalMessage;
    @JsonProperty("externalMessage")
    @JsonPropertyDescription("Human readable failure description for presentation in the UI to non-technical users.")
    private String externalMessage;
    @JsonProperty("metadata")
    @JsonPropertyDescription("Key-value pairs of relevant data")
    private Metadata metadata;
    @JsonProperty("stacktrace")
    @JsonPropertyDescription("Raw stacktrace associated with the failure.")
    private String stacktrace;
    @JsonProperty("retryable")
    @JsonPropertyDescription("True if it is known that retrying may succeed, e.g. for a transient failure. False if it is known that a retry will not succeed, e.g. for a configuration issue. If not set, retryable status is not well known.")
    private Boolean retryable;
    @JsonProperty("timestamp")
    private Long timestamp;
    private final static long serialVersionUID = -1485119682657564218L;

    @JsonProperty("failureOrigin")
    public FailureReasonForMigration.FailureOrigin getFailureOrigin() {
      return failureOrigin;
    }

    @JsonProperty("failureOrigin")
    public void setFailureOrigin(final FailureReasonForMigration.FailureOrigin failureOrigin) {
      this.failureOrigin = failureOrigin;
    }

    public FailureReasonForMigration withFailureOrigin(final FailureReasonForMigration.FailureOrigin failureOrigin) {
      this.failureOrigin = failureOrigin;
      return this;
    }

    @JsonProperty("failureType")
    public FailureReasonForMigration.FailureType getFailureType() {
      return failureType;
    }

    @JsonProperty("failureType")
    public void setFailureType(final FailureReasonForMigration.FailureType failureType) {
      this.failureType = failureType;
    }

    public FailureReasonForMigration withFailureType(final FailureReasonForMigration.FailureType failureType) {
      this.failureType = failureType;
      return this;
    }

    @JsonProperty("internalMessage")
    public String getInternalMessage() {
      return internalMessage;
    }

    @JsonProperty("internalMessage")
    public void setInternalMessage(final String internalMessage) {
      this.internalMessage = internalMessage;
    }

    public FailureReasonForMigration withInternalMessage(final String internalMessage) {
      this.internalMessage = internalMessage;
      return this;
    }

    @JsonProperty("externalMessage")
    public String getExternalMessage() {
      return externalMessage;
    }

    @JsonProperty("externalMessage")
    public void setExternalMessage(final String externalMessage) {
      this.externalMessage = externalMessage;
    }

    public FailureReasonForMigration withExternalMessage(final String externalMessage) {
      this.externalMessage = externalMessage;
      return this;
    }

    @JsonProperty("metadata")
    public Metadata getMetadata() {
      return metadata;
    }

    @JsonProperty("metadata")
    public void setMetadata(final Metadata metadata) {
      this.metadata = metadata;
    }

    public FailureReasonForMigration withMetadata(final Metadata metadata) {
      this.metadata = metadata;
      return this;
    }

    @JsonProperty("stacktrace")
    public String getStacktrace() {
      return stacktrace;
    }

    @JsonProperty("stacktrace")
    public void setStacktrace(final String stacktrace) {
      this.stacktrace = stacktrace;
    }

    public FailureReasonForMigration withStacktrace(final String stacktrace) {
      this.stacktrace = stacktrace;
      return this;
    }

    @JsonProperty("retryable")
    public Boolean getRetryable() {
      return retryable;
    }

    @JsonProperty("retryable")
    public void setRetryable(final Boolean retryable) {
      this.retryable = retryable;
    }

    public FailureReasonForMigration withRetryable(final Boolean retryable) {
      this.retryable = retryable;
      return this;
    }

    @JsonProperty("timestamp")
    public Long getTimestamp() {
      return timestamp;
    }

    @JsonProperty("timestamp")
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
      sb.append(((this.failureOrigin == null)?"<null>":this.failureOrigin));
      sb.append(',');
      sb.append("failureType");
      sb.append('=');
      sb.append(((this.failureType == null)?"<null>":this.failureType));
      sb.append(',');
      sb.append("internalMessage");
      sb.append('=');
      sb.append(((this.internalMessage == null)?"<null>":this.internalMessage));
      sb.append(',');
      sb.append("externalMessage");
      sb.append('=');
      sb.append(((this.externalMessage == null)?"<null>":this.externalMessage));
      sb.append(',');
      sb.append("metadata");
      sb.append('=');
      sb.append(((this.metadata == null)?"<null>":this.metadata));
      sb.append(',');
      sb.append("stacktrace");
      sb.append('=');
      sb.append(((this.stacktrace == null)?"<null>":this.stacktrace));
      sb.append(',');
      sb.append("retryable");
      sb.append('=');
      sb.append(((this.retryable == null)?"<null>":this.retryable));
      sb.append(',');
      sb.append("timestamp");
      sb.append('=');
      sb.append(((this.timestamp == null)?"<null>":this.timestamp));
      sb.append(',');
      if (sb.charAt((sb.length()- 1)) == ',') {
        sb.setCharAt((sb.length()- 1), ']');
      } else {
        sb.append(']');
      }
      return sb.toString();
    }

    @Override
    public int hashCode() {
      int result = 1;
      result = ((result* 31)+((this.retryable == null)? 0 :this.retryable.hashCode()));
      result = ((result* 31)+((this.metadata == null)? 0 :this.metadata.hashCode()));
      result = ((result* 31)+((this.stacktrace == null)? 0 :this.stacktrace.hashCode()));
      result = ((result* 31)+((this.failureOrigin == null)? 0 :this.failureOrigin.hashCode()));
      result = ((result* 31)+((this.failureType == null)? 0 :this.failureType.hashCode()));
      result = ((result* 31)+((this.internalMessage == null)? 0 :this.internalMessage.hashCode()));
      result = ((result* 31)+((this.externalMessage == null)? 0 :this.externalMessage.hashCode()));
      result = ((result* 31)+((this.timestamp == null)? 0 :this.timestamp.hashCode()));
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
      return (((((((((this.retryable == rhs.retryable)||((this.retryable!= null)&&this.retryable.equals(rhs.retryable)))&&((this.metadata == rhs.metadata)||((this.metadata!= null)&&this.metadata.equals(rhs.metadata))))&&((this.stacktrace == rhs.stacktrace)||((this.stacktrace!= null)&&this.stacktrace.equals(rhs.stacktrace))))&&((this.failureOrigin == rhs.failureOrigin)||((this.failureOrigin!= null)&&this.failureOrigin.equals(rhs.failureOrigin))))&&((this.failureType == rhs.failureType)||((this.failureType!= null)&&this.failureType.equals(rhs.failureType))))&&((this.internalMessage == rhs.internalMessage)||((this.internalMessage!= null)&&this.internalMessage.equals(rhs.internalMessage))))&&((this.externalMessage == rhs.externalMessage)||((this.externalMessage!= null)&&this.externalMessage.equals(rhs.externalMessage))))&&((this.timestamp == rhs.timestamp)||((this.timestamp!= null)&&this.timestamp.equals(rhs.timestamp))));
    }

    public enum FailureOrigin {

      UNKNOWN("unknown"),
      SOURCE("source"),
      DESTINATION("destination"),
      REPLICATION("replication"),
      REPLICATION_WORKER("replicationWorker"),
      PERSISTENCE("persistence"),
      NORMALIZATION("normalization"),
      DBT("dbt");
      private final String value;
      private final static Map<String, FailureReasonForMigration.FailureOrigin> CONSTANTS = new HashMap<String, FailureReasonForMigration.FailureOrigin>();

      static {
        for (final FailureReasonForMigration.FailureOrigin c: values()) {
          CONSTANTS.put(c.value, c);
        }
      }

      private FailureOrigin(final String value) {
        this.value = value;
      }

      @Override
      public String toString() {
        return this.value;
      }

      @JsonValue
      public String value() {
        return this.value;
      }

      @JsonCreator
      public static FailureReasonForMigration.FailureOrigin fromValue(final String value) {
        final FailureReasonForMigration.FailureOrigin constant = CONSTANTS.get(value);
        if (constant == null) {
          throw new IllegalArgumentException(value);
        } else {
          return constant;
        }
      }

    }


    public enum FailureType {

      UNKNOWN("unknown"),
      CONFIG_ERROR_OLD("configError"),
      SYSTEM_ERROR_OLD("systemError"),
      MANUAL_CANCELLATION_OLD("manualCancellation"),
      CONFIG_ERROR("config_error"),
      SYSTEM_ERROR("system_error"),
      MANUAL_CANCELLATION("manual_cancellation");
      private final String value;
      private final static Map<String, FailureReasonForMigration.FailureType> CONSTANTS = new HashMap<String, FailureReasonForMigration.FailureType>();

      static {
        for (final FailureReasonForMigration.FailureType c : values()) {
          CONSTANTS.put(c.value, c);
        }
      }

      private FailureType(final String value) {
        this.value = value;
      }

      @Override
      public String toString() {
        return this.value;
      }

      @JsonValue
      public String value() {
        return this.value;
      }

      @JsonCreator
      public static FailureReasonForMigration.FailureType fromValue(final String value) {
        final FailureReasonForMigration.FailureType constant = CONSTANTS.get(value);
        if (constant == null) {
          throw new IllegalArgumentException(value);
        } else {
          return constant;
        }
      }

    }

  }


  @JsonInclude(JsonInclude.Include.NON_NULL)
  @JsonPropertyOrder({
      "failures",
      "partialSuccess"
  })
  static
  class AttemptFailureSummaryForMigration implements Serializable {

    @JsonProperty("failures")
    @JsonPropertyDescription("Ordered list of failures that occurred during the attempt.")
    private List<FailureReasonForMigration> failures = new ArrayList<FailureReasonForMigration>();

    @JsonProperty("partialSuccess")
    @JsonPropertyDescription("True if the number of committed records for this attempt was greater than 0. False if 0 records were committed. Blank if number of committed records is unknown.")
    private Boolean partialSuccess;
    private final static long serialVersionUID = -9065693637249217586L;

    @JsonProperty("failures")
    public List<FailureReasonForMigration> getFailures() {
      return failures;
    }

    @JsonProperty("failures")
    public void setFailures(final List<FailureReasonForMigration> failures) {
      this.failures = failures;
    }

    public AttemptFailureSummaryForMigration withFailures(final List<FailureReasonForMigration> failures) {
      this.failures = failures;
      return this;
    }

    /**
     * True if the number of committed records for this attempt was greater than 0. False if 0 records were committed. Blank if number of committed
     * records is unknown.
     */
    @JsonProperty("partialSuccess")
    public Boolean getPartialSuccess() {
      return partialSuccess;
    }

    /**
     * True if the number of committed records for this attempt was greater than 0. False if 0 records were committed. Blank if number of committed
     * records is unknown.
     */
    @JsonProperty("partialSuccess")
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
      sb.append(((this.failures == null) ? "<null>" : this.failures));
      sb.append(',');
      sb.append("partialSuccess");
      sb.append('=');
      sb.append(((this.partialSuccess == null) ? "<null>" : this.partialSuccess));
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
      return (((this.partialSuccess == rhs.partialSuccess) || ((this.partialSuccess != null) && this.partialSuccess.equals(rhs.partialSuccess))) && (
          (this.failures == rhs.failures) || ((this.failures != null) && this.failures.equals(rhs.failures))));
    }

  }


}



