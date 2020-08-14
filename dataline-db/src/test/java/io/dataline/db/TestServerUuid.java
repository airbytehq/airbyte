package io.dataline.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.sql.SQLException;
import java.util.Optional;
import org.apache.commons.dbcp2.BasicDataSource;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.PostgreSQLContainer;

public class TestServerUuid {
  private static final JdbcDatabaseContainer POSTGRES_CONTAINER;
  private static final BasicDataSource CONNECTION_POOL;

  static {
    // todo: load image from env and don't hardcode absolute path
    POSTGRES_CONTAINER = new PostgreSQLContainer("postgres:13-alpine").withInitScript("schema.sql");
    POSTGRES_CONTAINER.start();

    CONNECTION_POOL =
        DatabaseHelper.getConnectionPool(
            POSTGRES_CONTAINER.getUsername(),
            POSTGRES_CONTAINER.getPassword(),
            POSTGRES_CONTAINER.getJdbcUrl());
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
