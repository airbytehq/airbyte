package io.airbyte.integrations.io.airbyte.integration_tests.sources.utils;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.json.Json;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;

public class MySqlSeeding {

  public static final String MYSQL_SYSTEM_DATABASE = "mysql";
  public static final String MYSQL_ROOT_USER = "root";
  private final DSLContext dslContext;

  public Database getDatabase() {
    return database;
  }

  private final Database database;
  private final String testDatabaseName;
  private final String testUser;
  private final String testUserPassword;
  private final JsonNode config;
  public static final String STREAM_NAME = "id_and_name";
  public static final String STREAM_NAME2 = "starships";


  public MySqlSeeding(Path configPath) {
    this(configPath, new HashMap<>());
  }

  public MySqlSeeding(Path configPath, Map<String, String> additionalConnectionProperties) {
    config = Jsons.deserialize(IOs.readFile(configPath));
    dslContext = getDslContextFromConfig(config, additionalConnectionProperties);
    database = new Database(dslContext);
    testDatabaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    testUser = config.get(JdbcUtils.USERNAME_KEY).asText();
    testUserPassword = config.get(JdbcUtils.PASSWORD_KEY).asText();
  }

  public JsonNode getConfig() {
    return config;
  }

  public boolean isCdc() {
    return Objects.equals(config.get("replication_method").get("method").asText(), "CDC");

  }
  private static DSLContext getDslContextFromConfig(JsonNode config, Map<String, String> additionalConnectionProperties) {
    return DSLContextFactory.create(
        MYSQL_ROOT_USER,
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(
            DatabaseDriver.MYSQL.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            MYSQL_SYSTEM_DATABASE
        ),
        SQLDialect.MYSQL,
        additionalConnectionProperties);
  }


  public void createAndUseTestDatabase() throws SQLException {
    database.query(ctx -> {
      ctx.execute("DROP DATABASE IF EXISTS `" + testDatabaseName + "`;");
      ctx.execute("CREATE DATABASE `" + testDatabaseName + "`;");
      ctx.execute("USE `" + testDatabaseName + "`;");
      return null;
    });
  }

  public void createTestTableAndData() throws SQLException {
    database.query(ctx -> {
      ctx.execute("DROP TABLE IF EXISTS " + STREAM_NAME + ";");
      ctx.execute("CREATE TABLE " + STREAM_NAME + "(id INTEGER, name VARCHAR(200));");
      ctx.execute("INSERT INTO " + STREAM_NAME + " (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
      ctx.execute("DROP TABLE IF EXISTS " + STREAM_NAME2 + ";");
      ctx.execute("CREATE TABLE " + STREAM_NAME2 + "(id INTEGER, name VARCHAR(200));");
      ctx.execute("INSERT INTO " +  STREAM_NAME2 + " (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
      return null;
    });
  }

  public void createCdcUser() throws SQLException {
    if (!Objects.equals(testUser, MYSQL_ROOT_USER)) {
      database.query(ctx -> {
        ctx.execute("DROP USER IF EXISTS '" + testUser + "'@'%' ;");
        ctx.execute("CREATE USER '" + testUser + "'@'%' IDENTIFIED BY '"+ testUserPassword + "';");
        ctx.execute(
            "GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO "
                + testUser + "@'%';");
        return null;
      });
    }
  }

  public void setUserRequireSsl() throws SQLException {
    if (!Objects.equals(testUser, MYSQL_ROOT_USER)) {
      database.query(ctx -> {
        ctx.execute("ALTER USER " + testUser + " REQUIRE SSL;");

        return null;
      });
    }
  }

  public void resetMaster() throws SQLException {
    // RESET MASTER removes all binary log files that are listed in the index file,
    // leaving only a single, empty binary log file with a numeric suffix of .000001
    database.query(ctx -> {
      ctx.execute("RESET MASTER;");
      return null;
    });

  }

  public void disableStrictMode() throws SQLException {
    database.query(ctx -> ctx.fetch("SET @@sql_mode=''"));
  }



  public void seed() throws SQLException {
    seed(true);
  }

  public void seed(boolean createTestData) throws SQLException {
    createAndUseTestDatabase();

    if (createTestData) {
      createTestTableAndData();
    }

    if (isCdc()) {
      createCdcUser();
    }
  }

  public void tearDown() throws SQLException {
    database.query(ctx -> {
      ctx.execute("DROP DATABASE IF EXISTS `" + testDatabaseName + "`;");
      if (!Objects.equals(testUser, MYSQL_ROOT_USER)) {
        ctx.execute("DROP USER IF EXISTS `" + testUser + "`;");
      }
      return null;
    });
    dslContext.close();
  }
}
