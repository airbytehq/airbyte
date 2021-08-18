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

package io.airbyte.db.instance;

import static io.airbyte.db.instance.configs.AirbyteConfigsTable.AIRBYTE_CONFIGS;
import static io.airbyte.db.instance.configs.AirbyteConfigsTable.CONFIG_BLOB;
import static io.airbyte.db.instance.configs.AirbyteConfigsTable.CONFIG_ID;
import static io.airbyte.db.instance.configs.AirbyteConfigsTable.CONFIG_TYPE;
import static io.airbyte.db.instance.configs.AirbyteConfigsTable.CREATED_AT;
import static io.airbyte.db.instance.configs.AirbyteConfigsTable.UPDATED_AT;
import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.UUID;
import org.jooq.JSONB;
import org.jooq.exception.DataAccessException;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public abstract class AbstractConfigsDatabaseTest {

  protected static PostgreSQLContainer<?> container;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  protected Database database;

  @BeforeEach
  public void setup() throws Exception {
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();

    // The configs database is considered ready only if there are some seed records.
    // So we need to create at least one record here.
    Timestamp timestamp = Timestamp.from(Instant.ofEpochMilli(System.currentTimeMillis()));
    database.transaction(ctx -> ctx.insertInto(AIRBYTE_CONFIGS)
        .set(CONFIG_ID, UUID.randomUUID().toString())
        .set(CONFIG_TYPE, "STANDARD_SOURCE_DEFINITION")
        .set(CONFIG_BLOB, JSONB.valueOf("{}"))
        .set(CREATED_AT, timestamp)
        .set(UPDATED_AT, timestamp)
        .execute());
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

}
