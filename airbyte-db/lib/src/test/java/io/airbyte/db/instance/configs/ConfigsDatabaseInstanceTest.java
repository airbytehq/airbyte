/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
