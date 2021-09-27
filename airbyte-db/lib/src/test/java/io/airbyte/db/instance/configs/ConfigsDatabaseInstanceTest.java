/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.OffsetDateTime;
import org.jooq.JSONB;
import org.jooq.exception.DataAccessException;
import org.junit.jupiter.api.Test;

class ConfigsDatabaseInstanceTest extends AbstractConfigsDatabaseTest {

  @Test
  public void testGet() throws Exception {
    // when the database has been initialized and loaded with data (in setup method), the get method
    // should return the database
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getInitialized();
    // check table
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS)));
  }

  @Test
  public void testGetAndInitialize() throws Exception {
    // check table
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS)));

    // check columns (if any of the column does not exist, the query will throw exception)
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CONFIG_ID.eq("ID"))));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CONFIG_TYPE.eq("TYPE"))));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CONFIG_BLOB.eq(JSONB.valueOf("{}")))));
    OffsetDateTime timestamp = OffsetDateTime.now();
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CREATED_AT.eq(timestamp))));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(UPDATED_AT.eq(timestamp))));

    // when the configs database has been initialized, calling getAndInitialize again will not change
    // anything
    String testSchema = "CREATE TABLE IF NOT EXISTS airbyte_test_configs(id BIGINT PRIMARY KEY);";
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl(), testSchema).getAndInitialize();
    // the airbyte_test_configs table does not exist
    assertThrows(DataAccessException.class, () -> database.query(ctx -> ctx.fetchExists(select().from("airbyte_test_configs"))));
  }

}
