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

package io.airbyte.server.migration;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import java.io.IOException;
import org.testcontainers.containers.PostgreSQLContainer;

public class StubAirbyteDB implements AutoCloseable {

  private final PostgreSQLContainer<?> container;
  private final Database database;

  public Database getDatabase() {
    return database;
  }

  public StubAirbyteDB() throws IOException {
    container =
        new PostgreSQLContainer<>("postgres:13-alpine")
            .withDatabaseName("airbyte")
            .withUsername("docker")
            .withPassword("docker");
    container.start();

    String jobsDatabaseSchema = MoreResources.readResource("migration/schema.sql");
    database = new JobsDatabaseInstance(
        container.getUsername(),
        container.getPassword(),
        container.getJdbcUrl(),
        jobsDatabaseSchema)
            .getAndInitialize();
  }

  @Override
  public void close() throws Exception {
    database.close();
    container.close();
  }

}
