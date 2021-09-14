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

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;

import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.instance.AbstractDatabaseTest;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.UUID;
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

  public Database getAndInitializeDatabase(String username, String password, String connectionString) throws IOException {
    Database database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();

    // The configs database is considered ready only if there are some seed records.
    // So we need to create at least one record here.
    OffsetDateTime timestamp = OffsetDateTime.now();
    new ExceptionWrappingDatabase(database).transaction(ctx -> ctx.insertInto(AIRBYTE_CONFIGS)
        .set(CONFIG_ID, UUID.randomUUID().toString())
        .set(CONFIG_TYPE, "STANDARD_SOURCE_DEFINITION")
        .set(CONFIG_BLOB, JSONB.valueOf("{}"))
        .set(CREATED_AT, timestamp)
        .set(UPDATED_AT, timestamp)
        .execute());
    return database;
  }

}
