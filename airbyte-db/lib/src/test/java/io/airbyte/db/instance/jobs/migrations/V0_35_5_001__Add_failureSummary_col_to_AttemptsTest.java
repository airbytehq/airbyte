/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs.migrations;

import io.airbyte.db.Database;
import io.airbyte.db.instance.jobs.AbstractJobsDatabaseTest;
import java.io.IOException;
import java.sql.SQLException;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class V0_35_5_001__Add_failureSummary_col_to_AttemptsTest extends AbstractJobsDatabaseTest {

  @Test
  public void test() throws SQLException, IOException {
    final Database database = getDatabase();
    final DSLContext context = DSL.using(database.getDataSource().getConnection());
    Assertions.assertFalse(failureSummaryColumnExists(context));
    V0_35_5_001__Add_failureSummary_col_to_Attempts.addFailureSummaryColumn(context);
    Assertions.assertTrue(failureSummaryColumnExists(context));
  }

  protected static boolean failureSummaryColumnExists(final DSLContext ctx) {
    return ctx.fetchExists(DSL.select()
        .from("information_schema.columns")
        .where(DSL.field("table_name").eq("attempts")
            .and(DSL.field("column_name").eq("failure_summary"))));
  }

}
