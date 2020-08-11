package io.dataline.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.io.IOException;
import java.sql.SQLException;
import org.junit.jupiter.api.Test;

public class TestDatabaseHelper {
  @Test
  void testTableCreation() throws SQLException, IOException {
    int numTables = DatabaseHelper.countTables();
    assertEquals(0, numTables);

    DatabaseHelper.initializeDatabase();

    numTables = DatabaseHelper.countTables();
    assertNotEquals(0, numTables);
  }
}
