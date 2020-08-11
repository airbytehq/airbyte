package io.dataline.db;

import java.sql.SQLException;

/*
The server UUID identifies a specific database installation of Dataline for analytics purposes.
 */
public class ServerUuid {
  public static String get() throws SQLException {
    return DatabaseHelper.executeQuery(
        "SELECT * FROM DATALINE_METADATA WHERE id = 'server-uuid'", rs -> rs.getString("value"));
  }
}
