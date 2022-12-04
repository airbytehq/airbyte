/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import com.google.common.annotations.VisibleForTesting;
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

public class V0_39_17_001__AddStreamDescriptorsToStateTable extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_39_17_001__AddStreamDescriptorsToStateTable.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());

    migrate(ctx);
  }

  @VisibleForTesting
  public static void migrate(final DSLContext ctx) {
    createStateTypeEnum(ctx);
    addStreamDescriptorFieldsToStateTable(ctx);
  }

  private static void createStateTypeEnum(final DSLContext ctx) {
    ctx.createType(StateType.NAME)
        .asEnum(Arrays.stream(StateType.values()).map(StateType::getLiteral).toList())
        .execute();
  }

  private static void addStreamDescriptorFieldsToStateTable(final DSLContext ctx) {
    final String STATE_TABLE = "state";

    ctx.alterTable(STATE_TABLE)
        .add(Arrays.asList(
            DSL.field("stream_name", SQLDataType.CLOB.nullable(true)),
            DSL.field("namespace", SQLDataType.CLOB.nullable(true)),
            // type defaults to LEGACY to first set the expected type of all existing states
            DSL.field("type", SQLDataType.VARCHAR.asEnumDataType(StateType.class).nullable(false).defaultValue(StateType.LEGACY)),
            DSL.constraint("state__connection_id__stream_name__namespace__uq")
                .unique(DSL.field("connection_id"), DSL.field("stream_name"), DSL.field("namespace"))))
        .execute();
  }

  public enum StateType implements EnumType {

    GLOBAL("GLOBAL"),
    STREAM("STREAM"),
    LEGACY("LEGACY");

    public static final String NAME = "state_type";

    StateType(String literal) {
      this.literal = literal;
    }

    @Override
    public String getLiteral() {
      return literal;
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

    private final String literal;

  }

}
