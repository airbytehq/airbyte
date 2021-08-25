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

import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.FlywayMigrationDatabase;
import java.io.IOException;

/**
 * Configs database for jOOQ code generation.
 */
public class ConfigsFlywayMigrationDatabase extends FlywayMigrationDatabase {

  public ConfigsFlywayMigrationDatabase() {
    super("src/main/resources/configs_database/schema_dump.txt");
  }

  @Override
  protected Database getAndInitializeDatabase(String username, String password, String connectionString) throws IOException {
    return new ConfigsDatabaseInstance(username, password, connectionString).getAndInitialize();

    // The configs database is considered ready only if there are some seed records.
    // So we need to create at least one record here.
    // Timestamp timestamp = Timestamp.from(Instant.ofEpochMilli(System.currentTimeMillis()));
    // new ExceptionWrappingDatabase(database).transaction(ctx -> ctx.insertInto(AIRBYTE_CONFIGS)
    // .set(CONFIG_ID, UUID.randomUUID().toString())
    // .set(CONFIG_TYPE, "STANDARD_SOURCE_DEFINITION")
    // .set(CONFIG_BLOB, JSONB.valueOf("{}"))
    // .set(CREATED_AT, timestamp)
    // .set(UPDATED_AT, timestamp)
    // .execute());
    // return database;
  }

  @Override
  protected DatabaseMigrator getDatabaseMigrator(Database database) {
    return new ConfigsDatabaseMigrator(database, ConfigsFlywayMigrationDatabase.class.getSimpleName());
  }

}
