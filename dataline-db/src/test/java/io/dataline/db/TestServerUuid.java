package io.dataline.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.sql.SQLException;
import java.util.Optional;
import org.apache.commons.dbcp2.BasicDataSource;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class TestServerUuid {
  private static final PostgreSQLContainer CONTAINER;
  private static final BasicDataSource CONNECTION_POOL;

  static {
    CONTAINER =
        new PostgreSQLContainer("postgres:13-alpine")
            .withDatabaseName("dataline")
            .withUsername("docker")
            .withPassword("docker");
    ;
    CONTAINER.start();

    try {
      CONTAINER.copyFileToContainer(
          MountableFile.forClasspathResource("schema.sql"), "/etc/init.sql");
      // execInContainer uses Docker's EXEC so it needs to be split up like this
      CONTAINER.execInContainer(
          "psql", "-d", "dataline", "-U", "docker", "-a", "-f", "/etc/init.sql");

    } catch (InterruptedException | IOException e) {
      throw new RuntimeException(e);
    }

    CONNECTION_POOL =
        DatabaseHelper.getConnectionPool(
            CONTAINER.getUsername(), CONTAINER.getPassword(), CONTAINER.getJdbcUrl());
  }

  @Test
  void testUuidFormat() throws SQLException, IOException {
    Optional<String> uuid = ServerUuid.get(CONNECTION_POOL);
    assertTrue(
        uuid.get()
            .matches(
                "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"));
  }

  @Test
  void testSameUuidOverInitializations() throws SQLException, IOException {
    Optional<String> uuid1 = ServerUuid.get(CONNECTION_POOL);
    Optional<String> uuid2 = ServerUuid.get(CONNECTION_POOL);

    assertEquals(uuid1, uuid2);
  }
}
