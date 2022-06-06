/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys.migrations;

import static org.jooq.impl.DSL.currentTimestamp;
import static org.jooq.impl.DSL.field;

import io.airbyte.db.instance.toys.ToysDatabaseConstants;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;

public class V0_30_4_001__Add_timestamp_columns extends BaseJavaMigration {

  @Override
  public void migrate(final Context context) {
    final DSLContext dsl = DSL.using(context.getConnection());
    dsl.alterTable(ToysDatabaseConstants.TABLE_NAME)
        .addColumn(field("created_at", SQLDataType.TIMESTAMP.defaultValue(currentTimestamp()).nullable(false)))
        .execute();
    dsl.alterTable(ToysDatabaseConstants.TABLE_NAME)
        .addColumn(field("updated_at", SQLDataType.TIMESTAMP.defaultValue(currentTimestamp()).nullable(false)))
        .execute();
  }

}
