/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import java.io.IOException;
import java.sql.SQLException;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Test;

public class V0_35_3_001__DropAirbyteConfigsTableTest extends AbstractConfigsDatabaseTest {

  @Test
  public void test() throws IOException, SQLException {
    final DSLContext context = getDslContext();
    assertTrue(airbyteConfigsExists(context));
    V0_35_3_001__DropAirbyteConfigsTable.dropTable(context);
    assertFalse(airbyteConfigsExists(context));
  }

  protected static boolean airbyteConfigsExists(final DSLContext ctx) {
    return ctx.fetchExists(select()
        .from("information_schema.tables")
        .where(DSL.field("table_name").eq("airbyte_configs")
            .and(DSL.field("table_schema").eq("public"))));
  }

}
