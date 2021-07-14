package io.airbyte.config.persistence;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;

import java.sql.Timestamp;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Table;

public class AirbyteConfigsTable {

  public static final String AIRBYTE_CONFIGS_TABLE_SCHEMA = "airbyte_configs_table.sql";

  public static final Table<Record> AIRBYTE_CONFIGS = table("airbyte_configs");
  public static final Field<String> CONFIG_ID = field("config_id", String.class);
  public static final Field<String> CONFIG_TYPE = field("config_type", String.class);
  public static final Field<JSONB> CONFIG_BLOB = field("config_blob", JSONB.class);
  public static final Field<Timestamp> CREATED_AT = field("created_at", Timestamp.class);
  public static final Field<Timestamp> UPDATED_AT = field("updated_at", Timestamp.class);

}
