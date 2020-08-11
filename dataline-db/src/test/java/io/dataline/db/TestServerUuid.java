package io.dataline.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.sql.SQLException;
import org.junit.jupiter.api.Test;

public class TestServerUuid {
  @Test
  void testUuidFormat() throws SQLException, IOException {
    DatabaseHelper.initializeDatabase();
    String uuid = ServerUuid.get();
    System.out.println("uuid = " + uuid);
    assertTrue(
        uuid.matches(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"));
  }

  @Test
  void testSameUuidOverInitializations() throws SQLException, IOException {
    DatabaseHelper.initializeDatabase();
    String uuid1 = ServerUuid.get();

    DatabaseHelper.initializeDatabase();
    String uuid2 = ServerUuid.get();

    assertEquals(uuid1, uuid2);
  }
}
