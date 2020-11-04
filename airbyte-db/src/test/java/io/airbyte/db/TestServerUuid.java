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

package io.airbyte.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.sql.SQLException;
import java.util.Optional;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class TestServerUuid {

  private static PostgreSQLContainer<?> container;
  private static Database database;

  @BeforeAll
  public static void dbSetup() throws IOException, InterruptedException {
    container =
        new PostgreSQLContainer<>("postgres:13-alpine")
            .withDatabaseName("airbyte")
            .withUsername("docker")
            .withPassword("docker");
    container.start();

    container.copyFileToContainer(MountableFile.forClasspathResource("schema.sql"), "/etc/init.sql");
    // execInContainer uses Docker's EXEC so it needs to be split up like this
    container.execInContainer("psql", "-d", "airbyte", "-U", "docker", "-a", "-f", "/etc/init.sql");

    database = Databases.createPostgresDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
  }

  @AfterAll
  public static void dbTeardown() throws Exception {
    database.close();
    container.close();
  }

  @Test
  void testUuidFormat() throws SQLException {
    Optional<String> uuid = ServerUuid.get(database);

    assertTrue(uuid.get().matches("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"));
  }

  @Test
  void testSameUuidOverInitializations() throws SQLException {
    Optional<String> uuid1 = ServerUuid.get(database);
    Optional<String> uuid2 = ServerUuid.get(database);

    assertEquals(uuid1, uuid2);
  }

}
