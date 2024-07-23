/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class V0_40_3_003__AddTokenToWorkspaceTest extends AbstractConfigsDatabaseTest {

  @Test
  void test() {
    final DSLContext context = getDslContext();

    // necessary to add workspace table
    V0_32_8_001__AirbyteConfigDatabaseDenormalization.migrate(context);

    Assertions.assertFalse(tokenColumnExists(context));

    V0_40_3_003__AddTokenToWorkspace.addTokenColumn(context);

    Assertions.assertTrue(tokenColumnExists(context));

  }

  protected static boolean tokenColumnExists(final DSLContext ctx) {
    return ctx.fetchExists(DSL.select()
        .from("information_schema.columns")
        .where(DSL.field("table_name").eq("workspace")
            .and(DSL.field("column_name").eq("token"))));
  }

}
