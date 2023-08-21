package io.airbyte.db.factory;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Map;
import java.util.Properties;

public class ConnectionFactory {
    public static Connection create(final String username,
                                    final String password,
                                    final Map<String, String> connectionProperties,
                                    final String jdbcConnectionString) {
        try {
            Properties properties = new Properties();
            properties.put("user", username);
            properties.put("password", password);
            connectionProperties.forEach((k, v) -> properties.put(k, v));

           return DriverManager.getConnection(jdbcConnectionString,
                    properties);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

}
