/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys.migrations;

import static org.jooq.impl.DSL.currentTimestamp;
import static org.jooq.impl.DSL.field;

import io.airbyte.db.instance.toys.ToysDatabaseInstance;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;

public class V0_30_4_001__Add_timestamp_columns extends BaseJavaMigration {

  @Override
  public void migrate(Context context) {
    DSLContext dsl = DSL.using(context.getConnection());
    dsl.alterTable(ToysDatabaseInstance.TABLE_NAME)
        .addColumn(field("created_at", SQLDataType.TIMESTAMP.defaultValue(currentTimestamp()).nullable(false)))
        .execute();
    dsl.alterTable(ToysDatabaseInstance.TABLE_NAME)
        .addColumn(field("updated_at", SQLDataType.TIMESTAMP.defaultValue(currentTimestamp()).nullable(false)))
        .execute();
  }

}
