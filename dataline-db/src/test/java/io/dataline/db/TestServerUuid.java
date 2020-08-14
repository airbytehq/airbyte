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
