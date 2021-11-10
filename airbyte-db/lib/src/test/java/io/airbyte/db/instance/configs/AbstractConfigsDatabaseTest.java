/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;

import io.airbyte.db.Database;
import io.airbyte.db.instance.AbstractDatabaseTest;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import java.io.IOException;
import java.time.OffsetDateTime;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Table;

public abstract class AbstractConfigsDatabaseTest extends AbstractDatabaseTest {

  public static final Table<Record> AIRBYTE_CONFIGS = table("airbyte_configs");
  public static final Field<String> CONFIG_ID = field("config_id", String.class);
  public static final Field<String> CONFIG_TYPE = field("config_type", String.class);
  public static final Field<JSONB> CONFIG_BLOB = field("config_blob", JSONB.class);
  public static final Field<OffsetDateTime> CREATED_AT = field("created_at", OffsetDateTime.class);
  public static final Field<OffsetDateTime> UPDATED_AT = field("updated_at", OffsetDateTime.class);

  @Override
  public Database getDatabase() throws IOException {
    return new TestDatabaseProviders(container).turnOffMigration().createNewConfigsDatabase();
  }

}
