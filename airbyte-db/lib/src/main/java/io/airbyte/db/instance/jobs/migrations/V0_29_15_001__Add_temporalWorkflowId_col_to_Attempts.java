package io.airbyte.db.instance.jobs.migrations;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;

public class V0_29_15_001__Add_temporalWorkflowId_col_to_Attempts extends BaseJavaMigration {

  @Override
  public void migrate(Context context) throws Exception {
    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    DSLContext ctx = DSL.using(context.getConnection());
    ctx.alterTable("attempts").addColumn(DSL.field("temporalWorkflowId", SQLDataType.VARCHAR.nullable(false).defaultValue("")))
        .execute();
  }

}
