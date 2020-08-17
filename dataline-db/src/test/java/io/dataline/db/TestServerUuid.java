/*
 * MIT License
 * 
 * Copyright (c) 2020 Dataline
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

package io.dataline.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.sql.SQLException;
import java.util.Optional;
import org.apache.commons.dbcp2.BasicDataSource;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class TestServerUuid {
  private static PostgreSQLContainer container;
  private static BasicDataSource connectionPool;

  @BeforeAll
  public static void dbSetup() {
    container =
        new PostgreSQLContainer("postgres:13-alpine")
            .withDatabaseName("dataline")
            .withUsername("docker")
            .withPassword("docker");
    ;
    container.start();

    try {
      container.copyFileToContainer(
          MountableFile.forClasspathResource("schema.sql"), "/etc/init.sql");
      // execInContainer uses Docker's EXEC so it needs to be split up like this
      container.execInContainer(
          "psql", "-d", "dataline", "-U", "docker", "-a", "-f", "/etc/init.sql");

    } catch (InterruptedException | IOException e) {
      throw new RuntimeException(e);
    }

    connectionPool =
        DatabaseHelper.getConnectionPool(
            container.getUsername(), container.getPassword(), container.getJdbcUrl());
  }

  @Test
  void testUuidFormat() throws SQLException, IOException {
    Optional<String> uuid = ServerUuid.get(connectionPool);
    assertTrue(
        uuid.get()
            .matches(
                "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"));
  }

  @Test
  void testSameUuidOverInitializations() throws SQLException, IOException {
    Optional<String> uuid1 = ServerUuid.get(connectionPool);
    Optional<String> uuid2 = ServerUuid.get(connectionPool);

    assertEquals(uuid1, uuid2);
  }
}
