/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys.migrations;

import static org.jooq.impl.DSL.field;

import io.airbyte.db.instance.toys.ToysDatabaseConstants;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;

public class V0_30_4_002__Remove_updated_at_column extends BaseJavaMigration {

  @Override
  public void migrate(final Context context) {
    final DSLContext dsl = DSL.using(context.getConnection());
    dsl.alterTable(ToysDatabaseConstants.TABLE_NAME)
        .dropColumn(field("updated_at"))
        .execute();
  }

}
