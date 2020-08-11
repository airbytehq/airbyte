package io.dataline.conduit.commons.db;

import java.sql.SQLException;

public class ClientUuid {
    public static String get() throws SQLException {
        return DatabaseHelper.executeQuery(
                "SELECT * FROM CONDUIT_METADATA WHERE key = 'server-uuid'",
                rs -> rs.getString("value")
        );
    }
}
