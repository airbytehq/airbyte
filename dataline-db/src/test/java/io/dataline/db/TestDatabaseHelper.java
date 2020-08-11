package io.dataline.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.io.IOException;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.Set;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class TestDatabaseHelper {
  @BeforeEach
  void dropDb() throws SQLException {
    Set<String> tables =
        DatabaseHelper.executeQuery(
            "SELECT * FROM sqlite_master WHERE (type ='table' AND name NOT LIKE 'sqlite_%');",
            rs -> {
              Set<String> result = new HashSet<>();

              while (rs.next()) {
                result.add(rs.getString("tbl_name"));
              }

              return result;
            });

    for (String table : tables) {
      DatabaseHelper.execute("DROP TABLE " + table);
    }
  }

  @Test
  void testTableCreation() throws SQLException, IOException {
    int numTables = DatabaseHelper.countTables();
    System.out.println("numTables = " + numTables);
    assertEquals(0, numTables);

    DatabaseHelper.initializeDatabase();

    numTables = DatabaseHelper.countTables();
    assertNotEquals(0, numTables);
  }
}
