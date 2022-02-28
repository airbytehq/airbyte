package io.airbyte.db.instance.jobs.migrations;

import static org.jooq.impl.DSL.asterisk;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Metadata;
import io.airbyte.db.Database;
import io.airbyte.db.instance.jobs.migrations.V0_35_40_001__MigrateFailureReasonEnumValues.AttemptFailureSummaryForMigration;
import io.airbyte.db.instance.jobs.migrations.V0_35_40_001__MigrateFailureReasonEnumValues.FailureReasonForMigration;
import io.airbyte.db.instance.jobs.migrations.V0_35_40_001__MigrateFailureReasonEnumValues.FailureReasonForMigration.FailureOrigin;
import io.airbyte.db.instance.jobs.migrations.V0_35_40_001__MigrateFailureReasonEnumValues.FailureReasonForMigration.FailureType;
import io.airbyte.db.instance.jobs.AbstractJobsDatabaseTest;
import java.util.List;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.junit.jupiter.api.Test;

public class V0_35_40_001_MigrateFailureReasonEnumValues_Test extends AbstractJobsDatabaseTest {

  private static int currJobId = 1;
  private static final long timeNowMillis = System.currentTimeMillis();

  // create pairs of old failure reasons and their fixed versions.
  private static final FailureReasonForMigration originReplicationWorker = baseFailureReason().withFailureOrigin(FailureOrigin.REPLICATION_WORKER);
  private static final FailureReasonForMigration fixedOriginReplicationWorker = baseFailureReason().withFailureOrigin(FailureOrigin.REPLICATION);

  private static final FailureReasonForMigration originUnknown = baseFailureReason().withFailureOrigin(FailureOrigin.UNKNOWN);
  private static final FailureReasonForMigration fixedOriginUnknown = baseFailureReason().withFailureOrigin(null);

  private static final FailureReasonForMigration typeManualCancellation = baseFailureReason().withFailureType(FailureType.MANUAL_CANCELLATION_OLD);
  private static final FailureReasonForMigration fixedTypeManualCancellation = baseFailureReason().withFailureType(FailureType.MANUAL_CANCELLATION);

  private static final FailureReasonForMigration typeSystemError = baseFailureReason().withFailureType(FailureType.SYSTEM_ERROR_OLD);
  private static final FailureReasonForMigration fixedTypeSystemError = baseFailureReason().withFailureType(FailureType.SYSTEM_ERROR);

  private static final FailureReasonForMigration typeConfigError = baseFailureReason().withFailureType(FailureType.CONFIG_ERROR_OLD);
  private static final FailureReasonForMigration fixedTypeConfigError = baseFailureReason().withFailureType(FailureType.CONFIG_ERROR);

  private static final FailureReasonForMigration typeUnknown = baseFailureReason().withFailureType(FailureType.UNKNOWN);
  private static final FailureReasonForMigration fixedTypeUnknown = baseFailureReason().withFailureType(null);

  private static final FailureReasonForMigration noChangeNeeded = baseFailureReason().withFailureOrigin(FailureOrigin.SOURCE);

  // create failure summaries containing failure reasons that need fixing.
  // mixing in noChangeNeeded reasons in different spots to make sure the migration properly leaves those untouched.
  private static final AttemptFailureSummaryForMigration summaryFixReplicationOrigin = getFailureSummary(noChangeNeeded, originReplicationWorker);
  private static final AttemptFailureSummaryForMigration summaryFixReplicationOriginAndManualCancellationType = getFailureSummary(originReplicationWorker, typeManualCancellation, noChangeNeeded);
  private static final AttemptFailureSummaryForMigration summaryFixUnknownOriginAndUnknownType = getFailureSummary(originUnknown, noChangeNeeded, typeUnknown);
  private static final AttemptFailureSummaryForMigration summaryFixMultipleSystemErrorType = getFailureSummary(typeSystemError, typeSystemError);
  private static final AttemptFailureSummaryForMigration summaryFixConfigErrorType = getFailureSummary(typeConfigError);
  private static final AttemptFailureSummaryForMigration summaryNoChangeNeeded = getFailureSummary(noChangeNeeded, noChangeNeeded);

  // define attempt ids corresponding to each summary above
  private static final Long attemptIdForFixReplicationOrigin = 1L;
  private static final Long attemptIdForFixReplicationOriginAndManualCancellationType = 2L;
  private static final Long attemptIdForFixUnknownOriginAndUnknownType = 3L;
  private static final Long attemptIdForFixMultipleSystemErrorType = 4L;
  private static final Long attemptIdForFixConfigErrorType = 5L;
  private static final Long attemptIdForNoChangeNeeded = 6L;

  // create expected fixed failure summaries after migration.
  private static final AttemptFailureSummaryForMigration expectedSummaryFixReplicationOrigin =
      getFailureSummary(noChangeNeeded, fixedOriginReplicationWorker);
  private static final AttemptFailureSummaryForMigration expectedSummaryFixReplicationOriginAndManualCancellationType =
      getFailureSummary(fixedOriginReplicationWorker, fixedTypeManualCancellation, noChangeNeeded);
  private static final AttemptFailureSummaryForMigration expectedSummaryFixUnknownOriginAndUnknownType =
      getFailureSummary(fixedOriginUnknown, noChangeNeeded, fixedTypeUnknown);
  private static final AttemptFailureSummaryForMigration expectedSummaryFixMultipleSystemErrorType =
      getFailureSummary(fixedTypeSystemError, fixedTypeSystemError);
  private static final AttemptFailureSummaryForMigration expectedSummaryFixConfigErrorType =
      getFailureSummary(fixedTypeConfigError);
  private static final AttemptFailureSummaryForMigration expectedSummaryNoChangeNeeded =
      getFailureSummary(noChangeNeeded, noChangeNeeded);

  @Test
  public void test() throws Exception {
    final Database database = getDatabase();
    final DSLContext ctx = DSL.using(database.getDataSource().getConnection());

    V0_35_5_001__Add_failureSummary_col_to_Attempts.migrate(ctx);

    addRecordsWithOldEnumValues(ctx);

    V0_35_40_001__MigrateFailureReasonEnumValues.updateRecordsWithNewEnumValues(ctx);

    verifyEnumValuesFixed(ctx);
  }


  private static void addRecordsWithOldEnumValues(final DSLContext ctx) {
    insertAttemptWithSummary(ctx, attemptIdForFixReplicationOrigin, summaryFixReplicationOrigin);
    insertAttemptWithSummary(ctx, attemptIdForFixReplicationOriginAndManualCancellationType, summaryFixReplicationOriginAndManualCancellationType);
    insertAttemptWithSummary(ctx, attemptIdForFixUnknownOriginAndUnknownType, summaryFixUnknownOriginAndUnknownType);
    insertAttemptWithSummary(ctx, attemptIdForFixMultipleSystemErrorType, summaryFixMultipleSystemErrorType);
    insertAttemptWithSummary(ctx, attemptIdForFixConfigErrorType, summaryFixConfigErrorType);
    insertAttemptWithSummary(ctx, attemptIdForNoChangeNeeded, summaryNoChangeNeeded);
  }

  private static void verifyEnumValuesFixed(final DSLContext ctx) {
    assertEquals(expectedSummaryFixReplicationOrigin, fetchFailureSummary(ctx, attemptIdForFixReplicationOrigin));
    assertEquals(expectedSummaryFixReplicationOriginAndManualCancellationType, fetchFailureSummary(ctx, attemptIdForFixReplicationOriginAndManualCancellationType));
    assertEquals(expectedSummaryFixUnknownOriginAndUnknownType, fetchFailureSummary(ctx, attemptIdForFixUnknownOriginAndUnknownType));
    assertEquals(expectedSummaryFixMultipleSystemErrorType, fetchFailureSummary(ctx, attemptIdForFixMultipleSystemErrorType));
    assertEquals(expectedSummaryFixConfigErrorType, fetchFailureSummary(ctx, attemptIdForFixConfigErrorType));
    assertEquals(expectedSummaryNoChangeNeeded, fetchFailureSummary(ctx, attemptIdForNoChangeNeeded));

  }

  private static void insertAttemptWithSummary(final DSLContext ctx, final Long attemptId, final AttemptFailureSummaryForMigration summary) {
    ctx.insertInto(DSL.table("attempts"))
        .columns(
            DSL.field("id"),
            DSL.field("failure_summary"),
            DSL.field("job_id"),
            DSL.field("attempt_number"))
        .values(
            attemptId,
            JSONB.valueOf(Jsons.serialize(summary)),
            currJobId,
            1
        ).execute();

    currJobId++;
  }

  private static AttemptFailureSummaryForMigration fetchFailureSummary(final DSLContext ctx, final Long attemptId) {
    final Record record = ctx.fetchOne(DSL.select(asterisk())
        .from(DSL.table("attempts"))
        .where(DSL.field("id").eq(attemptId))
    );

    return Jsons.deserialize(
        record.get(DSL.field("failure_summary", SQLDataType.JSONB.nullable(true))).data(),
        AttemptFailureSummaryForMigration.class);

  }

  private static FailureReasonForMigration baseFailureReason() {
    return new FailureReasonForMigration()
        .withInternalMessage("some internal message")
        .withExternalMessage("some external message")
        .withRetryable(false)
        .withTimestamp(timeNowMillis)
        .withStacktrace("some stacktrace")
        .withMetadata(new Metadata().withAdditionalProperty("key1", "value1"));
  }

  private static AttemptFailureSummaryForMigration getFailureSummary(final FailureReasonForMigration ...failureReasons) {
    return new AttemptFailureSummaryForMigration()
        .withPartialSuccess(false)
        .withFailures(List.of(failureReasons));
  }
}
