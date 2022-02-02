/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import java.io.IOException;
import java.sql.SQLException;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Test;

public class V0_35_16_001__CreateFeatureFlagTable_Test extends AbstractConfigsDatabaseTest {

  @Test
  public void test() throws IOException, SQLException {
    final Database database = getDatabase();
    final DSLContext context = DSL.using(database.getDataSource().getConnection());
    assertFalse(airbyteFeatureFlags(context));
    V0_35_16_001__CreateFeatureFlagTable migration = new V0_35_16_001__CreateFeatureFlagTable();
    migration.createTable(context);
    assertTrue(airbyteFeatureFlags(context));
  }

  protected static boolean airbyteFeatureFlags(final DSLContext ctx) {
    return ctx.fetchExists(select()
        .from("information_schema.tables")
        .where(DSL.field("table_name").eq("feature_flag")
            .and(DSL.field("table_schema").eq("public"))));
  }

}
