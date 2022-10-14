/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Collectors;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

import org.jooq.DSLContext;
import org.jooq.SQLDialect;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BitDotIoDestinationAcceptanceTest extends DestinationAcceptanceTest {
  public class BitDotIoConfig {
      private String username = "";
      private String database = "";
      private String password = "";
      public String getUsername() {
        return username;
      }
      public String getDatabase() {
        return database;
      }
      public String getPassword() {
        return password;
      }
    public BitDotIoConfig(String username, String database, String password) 
    {
      this.username = username;
      this.database = database;
      this.password = password;
    }

    public String getJdbcUrl() {
        String jdbcUrl = "";
        try {
          jdbcUrl = "jdbc:postgresql://db.bit.io:5432" + "/" + URLEncoder.encode(database, "UTF-8") + "?sslmode=require";
        } catch (UnsupportedEncodingException e) {
          // Should never happen
          e.printStackTrace();
        }
        return jdbcUrl;
    }
  }


  private static final Logger LOGGER = LoggerFactory.getLogger(BitDotIoDestinationAcceptanceTest.class);
  private BitDotIoConfig cfg;
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  protected static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  protected static final String CONFIG_BITIO_USERNAME = "username";
  protected static final String CONFIG_BITIO_DATABASE = "database";
  protected static final String CONFIG_BITIO_CONNECT_PASSWORD = "connect_password";

  @Override
  protected String getImageName() {
    return "airbyte/destination-bitdotio:dev";
  }

  @Override
  protected JsonNode getConfig() {

    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "db.bit.io")
        .put(JdbcUtils.PORT_KEY, 5432)
        .put(JdbcUtils.SCHEMA_KEY, "public")
        .put(JdbcUtils.USERNAME_KEY, cfg.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, cfg.getPassword())
        .put(JdbcUtils.DATABASE_KEY, cfg.getDatabase())
        .put(JdbcUtils.SSL_KEY, true )
        .put("sslmode", "require" )
        .put("ssl_mode", ImmutableMap.builder().put("mode", "require").build())
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "db.bit.io")
        .put(JdbcUtils.PORT_KEY, 5432)
        .put(JdbcUtils.SCHEMA_KEY, "public")
        .put(JdbcUtils.USERNAME_KEY, cfg.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, "wrong password")
        .put(JdbcUtils.DATABASE_KEY, cfg.getDatabase())
        .put(JdbcUtils.SSL_KEY, true)
        .put("sslmode", "require" )
        .put("ssl_mode", ImmutableMap.builder().put("mode", "require").build())
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean supportsNormalization() {
    return true;
  }

  @Override
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
      result.add(resolved.toUpperCase());
    }
    return result;
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    try (final DSLContext dslContext = DSLContextFactory.create(
        cfg.getUsername(),
        cfg.getPassword(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        cfg.getJdbcUrl(),
        SQLDialect.POSTGRES)) {
      return new Database(dslContext)
          .query(
              ctx -> ctx
                  .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                  .stream()
                  .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                  .map(Jsons::deserialize)
                  .collect(Collectors.toList()));
    }
  }
  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a bit.io query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String fullConfigAsString = Files.readString(CREDENTIALS_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
    final String username = credentialsJson.get(CONFIG_BITIO_USERNAME).asText();
    final String database = credentialsJson.get(CONFIG_BITIO_DATABASE).asText();
    final String password = credentialsJson.get(CONFIG_BITIO_CONNECT_PASSWORD).asText();

    this.cfg = new BitDotIoConfig(username, database, password) ;
  }
  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    try (final DSLContext dslContext = DSLContextFactory.create(
        cfg.getUsername(),
        cfg.getPassword(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        cfg.getJdbcUrl(),
        SQLDialect.POSTGRES)) {

      Database db = new Database(dslContext);
      List<JsonNode> tables = db.query(
              ctx -> ctx
                  .fetch( "SELECT table_name FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema not IN ('pg_catalog', 'information_schema');")
                  .stream()
                  .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                  .map(Jsons::deserialize)
                  .collect(Collectors.toList()));
        for (JsonNode node : tables) {
          db.query(ctx -> ctx.fetch(String.format("DROP TABLE IF EXISTS %s CASCADE", node.get("table_name"))));
        }
      List<JsonNode> schemas = db.query(
              ctx -> ctx
                  .fetch( "SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema not IN ('public', 'pg_catalog', 'information_schema');")
                  .stream()
                  .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                  .map(Jsons::deserialize)
                  .collect(Collectors.toList()));
        for (JsonNode node : schemas) {
          db.query(ctx -> ctx.fetch(String.format("DROP SCHEMA IF EXISTS %s CASCADE", node.get("table_schema"))));
        }
    } catch (SQLException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }
    LOGGER.info("Finished acceptance test for bit.io");
  }
}