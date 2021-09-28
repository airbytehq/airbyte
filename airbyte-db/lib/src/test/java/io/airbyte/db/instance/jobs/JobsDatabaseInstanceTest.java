/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.jooq.exception.DataAccessException;
import org.junit.jupiter.api.Test;

class JobsDatabaseInstanceTest extends AbstractJobsDatabaseTest {

  @Test
  public void testGet() throws Exception {
    // when the database has been initialized and loaded with data (in setup method), the get method
    // should return the database
    database = new JobsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getInitialized();
    // check table
    database.query(ctx -> ctx.fetchExists(select().from("airbyte_metadata")));
  }

  @Test
  public void testGetAndInitialize() throws Exception {
    // check table
    database.query(ctx -> ctx.fetchExists(select().from("jobs")));
    database.query(ctx -> ctx.fetchExists(select().from("attempts")));
    database.query(ctx -> ctx.fetchExists(select().from("airbyte_metadata")));

    // when the jobs database has been initialized, calling getAndInitialize again will not change
    // anything
    String testSchema = "CREATE TABLE IF NOT EXISTS airbyte_test_metadata(id BIGINT PRIMARY KEY);";
    database = new JobsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl(), testSchema).getAndInitialize();
    // the airbyte_test_metadata table does not exist
    assertThrows(DataAccessException.class, () -> database.query(ctx -> ctx.fetchExists(select().from("airbyte_test_metadata"))));
  }

}
