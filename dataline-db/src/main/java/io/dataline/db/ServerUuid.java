package io.dataline.db;

import java.sql.SQLException;

public class ServerUuid {
  public static String get() throws SQLException {
    return DatabaseHelper.executeQuery(
        "SELECT * FROM DATALINE_METADATA WHERE id = 'server-uuid'", rs -> rs.getString("value"));
  }
}
