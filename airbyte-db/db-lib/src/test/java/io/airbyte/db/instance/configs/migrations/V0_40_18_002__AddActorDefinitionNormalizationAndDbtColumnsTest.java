/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class V0_40_18_002__AddActorDefinitionNormalizationAndDbtColumnsTest extends AbstractConfigsDatabaseTest {

  @BeforeEach
  void beforeEach() {
    final Flyway flyway =
        FlywayFactory.create(dataSource, "V0_40_18_001__AddInvalidProtocolFlagToConnections", ConfigsDatabaseMigrator.DB_IDENTIFIER,
            ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    final ConfigsDatabaseMigrator configsDbMigrator = new ConfigsDatabaseMigrator(database, flyway);

    final BaseJavaMigration previousMigration = new V0_40_18_001__AddInvalidProtocolFlagToConnections();
    final DevDatabaseMigrator devConfigsDbMigrator = new DevDatabaseMigrator(configsDbMigrator, previousMigration.getVersion());
    devConfigsDbMigrator.createBaseline();
  }

  @Test
  void test() throws Exception {
    final DSLContext context = getDslContext();
    assertFalse(columnExists(context, "normalization_repository"));
    assertFalse(columnExists(context, "normalization_tag"));
    assertFalse(columnExists(context, "supports_dbt"));
    V0_40_18_002__AddActorDefinitionNormalizationAndDbtColumns.addNormalizationRepositoryColumn(context);
    assertTrue(columnExists(context, "normalization_repository"));
    V0_40_18_002__AddActorDefinitionNormalizationAndDbtColumns.addNormalizationTagColumn(context);
    assertTrue(columnExists(context, "normalization_tag"));
    V0_40_18_002__AddActorDefinitionNormalizationAndDbtColumns.addSupportsDbtColumn(context);
    assertTrue(columnExists(context, "supports_dbt"));
  }

  static boolean columnExists(final DSLContext ctx, final String columnName) {
    return ctx.fetchExists(DSL.select()
        .from("information_schema.columns")
        .where(DSL.field("table_name").eq("actor_definition")
            .and(DSL.field("column_name").eq(columnName))));
  }

}
