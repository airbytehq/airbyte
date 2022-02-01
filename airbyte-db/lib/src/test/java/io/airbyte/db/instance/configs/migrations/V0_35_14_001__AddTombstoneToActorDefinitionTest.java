package io.airbyte.db.instance.configs.migrations;

import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import java.io.IOException;
import java.sql.SQLException;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class V0_35_14_001__AddTombstoneToActorDefinitionTest extends AbstractConfigsDatabaseTest {
  @Test
  public void test() throws SQLException, IOException {

    final Database database = getDatabase();
    final DSLContext context = DSL.using(database.getDataSource().getConnection());

    // necessary to add actor_definition table
    V0_32_8_001__AirbyteConfigDatabaseDenormalization.migrate(context);

    Assertions.assertFalse(tombstoneColumnExists(context));
    V0_35_14_001__AddTombstoneToActorDefinition.addTombstoneColumn(context);
    Assertions.assertTrue(tombstoneColumnExists(context));
  }

  protected static boolean tombstoneColumnExists(final DSLContext ctx) {
    return ctx.fetchExists(DSL.select()
        .from("information_schema.columns")
        .where(DSL.field("table_name").eq("actor_definition")
            .and(DSL.field("column_name").eq("tombstone"))));
  }
}
