/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import java.io.IOException;
import java.sql.SQLException;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Test;

public class V0_40_3_001__RemoveActorForeignKeyFromOauthParamsTableTest extends AbstractConfigsDatabaseTest {

  @Test
  void test() throws IOException, SQLException {
    final DSLContext context = getDslContext();
    V0_32_8_001__AirbyteConfigDatabaseDenormalization.migrate(context);

    assertTrue(foreignKeyExists(context));
    V0_40_3_001__RemoveActorForeignKeyFromOauthParamsTable.removeActorDefinitionForeignKey(context);
    assertFalse(foreignKeyExists(context));
  }

  protected static boolean foreignKeyExists(final DSLContext ctx) {
    return ctx.fetchExists(DSL.select()
        .from("information_schema.table_constraints")
        .where(DSL.field("table_name").eq("actor_oauth_parameter")
            .and(DSL.field("constraint_name").eq("actor_oauth_parameter_actor_definition_id_fkey"))));
  }

}
