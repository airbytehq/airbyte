/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.db.Database;
import org.jooq.exception.DataAccessException;
import org.junit.jupiter.api.Test;

class JobsDatabaseInstanceTest extends AbstractJobsDatabaseTest {

  @Test
  public void testGet() throws Exception {
    final Database database = new JobsDatabaseInstance(getDslContext()).getInitialized();
    // check table
    database.query(ctx -> ctx.fetchExists(select().from("airbyte_metadata")));
  }

  @Test
  public void testGetAndInitialize() throws Exception {
    final Database database = new JobsDatabaseInstance(getDslContext()).getInitialized();

    // check table
    database.query(ctx -> ctx.fetchExists(select().from("jobs")));
    database.query(ctx -> ctx.fetchExists(select().from("attempts")));
    database.query(ctx -> ctx.fetchExists(select().from("airbyte_metadata")));

    // when the jobs database has been initialized, calling getAndInitialize again will not change
    // anything
    final String testSchema = "CREATE TABLE IF NOT EXISTS airbyte_test_metadata(id BIGINT PRIMARY KEY);";
    final Database database2 = new JobsDatabaseInstance(getDslContext(), testSchema).getAndInitialize();
    // the airbyte_test_metadata table does not exist
    assertThrows(DataAccessException.class, () -> database2.query(ctx -> ctx.fetchExists(select().from("airbyte_test_metadata"))));
  }

}
