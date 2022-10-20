/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import java.util.Arrays;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.Catalog;
import org.jooq.DSLContext;
import org.jooq.EnumType;
import org.jooq.Schema;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.jooq.impl.SchemaImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_40_11_001__AddGeographyColumnToConnections extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_11_001__AddGeographyColumnToConnections.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());

    addGeographyEnumDataTypes(ctx);
    addGeographyColumnToConnection(ctx);
    addGeographyColumnToWorkspace(ctx);
  }

  private static void addGeographyEnumDataTypes(final DSLContext ctx) {
    ctx.createType(GeographyType.NAME)
        .asEnum(Arrays.stream(GeographyType.values()).map(GeographyType::getLiteral).toList())
        .execute();
  }

  private static void addGeographyColumnToConnection(final DSLContext ctx) {
    ctx.alterTable("connection")
        .addColumnIfNotExists(DSL.field(
            "geography",
            SQLDataType.VARCHAR.asEnumDataType(GeographyType.class).nullable(false).defaultValue(GeographyType.AUTO)))
        .execute();
  }

  private static void addGeographyColumnToWorkspace(final DSLContext ctx) {
    ctx.alterTable("workspace")
        .addColumnIfNotExists(DSL.field(
            "geography",
            SQLDataType.VARCHAR.asEnumDataType(GeographyType.class).nullable(false).defaultValue(GeographyType.AUTO)))
        .execute();
  }

  public enum GeographyType implements EnumType {

    AUTO("AUTO"),
    US("US"),
    EU("EU");

    private final String literal;
    public static final String NAME = "geography_type";

    GeographyType(final String literal) {
      this.literal = literal;
    }

    @Override
    public Catalog getCatalog() {
      return getSchema().getCatalog();
    }

    @Override
    public Schema getSchema() {
      return new SchemaImpl(DSL.name("public"));
    }

    @Override
    public String getName() {
      return NAME;
    }

    @Override
    public String getLiteral() {
      return literal;
    }

  }

}
