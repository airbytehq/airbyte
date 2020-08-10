package io.dataline.conduit.commons.db;

import com.google.common.io.Resources;
import io.dataline.conduit.commons.env.Env;
import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class DatabaseHelper {
    private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseHelper.class);

    private static BasicDataSource connectionPool;

    public static synchronized BasicDataSource getConnectionPool() {
        if(connectionPool == null) {
            connectionPool = new BasicDataSource();
            connectionPool.setDriverClassName("org.sqlite.JDBC");
            connectionPool.setUrl(Env.isTest() ? "jdbc:sqlite::memory:" : "jdbc:sqlite:conduit.db");
            connectionPool.setInitialSize(Env.isTest() ? 1 : 5);
        }

        return connectionPool;
    }

    private static List<String> getSchema() throws IOException {
        // TODO: use com.ibatis.common.jdbc.ScriptRunner
        try (InputStream stream = Resources.getResource("schema.sql").openStream()) {
            InputStreamReader streamReader = new InputStreamReader(stream, StandardCharsets.UTF_8);
            BufferedReader bufferedReader = new BufferedReader(streamReader);
            return bufferedReader.lines().collect(Collectors.toCollection(ArrayList::new));
        }
    }

    protected static int countTables() throws SQLException {
        return executeQuery(
                "SELECT COUNT(*) FROM sqlite_master WHERE (type ='table' AND name NOT LIKE 'sqlite_%');",
                rs -> rs.getInt(1)
        );
    }

    public static void initializeDatabase() throws IOException, SQLException {
        if(countTables() == 0) {
            for (String line : getSchema()) {
                LOGGER.info("Executing SQL Schema: " + line);
                execute(line);
            }
        } else {
            LOGGER.warn("Skipping initializeDatabase because some tables already exist!");
        }
    }

    public static boolean execute(String sql) throws SQLException {
        try (Connection connection = getConnectionPool().getConnection()) {
            Statement statement = connection.createStatement();
            return statement.execute(sql);
        }
    }

    public static <T> T executeQuery(String sql, ResultSetTransformer<T> transform) throws SQLException {
        try (Connection connection = getConnectionPool().getConnection()) {
            Statement statement = connection.createStatement();
            return transform.apply(statement.executeQuery(sql));
        }
    }
}
