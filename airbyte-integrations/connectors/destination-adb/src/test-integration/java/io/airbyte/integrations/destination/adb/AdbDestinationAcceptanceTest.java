/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.adb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTestUtils;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import org.apache.commons.lang3.ObjectUtils;
import org.jooq.DSLContext;
import org.jooq.Record;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;

public class AdbDestinationAcceptanceTest extends DestinationAcceptanceTest {

  protected final ObjectMapper mapper = new ObjectMapper();

  protected MySQLContainer<?> db;

  private final StandardNameTransformer namingResolver = new MySQLNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-adb:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
            .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db))
            .put(JdbcUtils.USERNAME_KEY, db.getUsername())
            .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
            .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
            .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(db))
            .put(JdbcUtils.SSL_KEY, false)
            .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final ObjectNode config = (ObjectNode) getConfig();
    config.put(JdbcUtils.PASSWORD_KEY, "wrong password");
    return config;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
          throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
            .stream()
            .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA))
            .collect(Collectors.toList());
  }

  @Override
  protected void setup(TestDestinationEnv testEnv, HashSet<String> TEST_SCHEMAS) {
    db = new MySQLContainer<>("mysql:8.0");
    db.start();
    setLocalInFileToTrue();
    revokeAllPermissions();
    grantCorrectPermissions();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

  private void setLocalInFileToTrue() {
    executeQuery("set global local_infile=true");
  }

  private void revokeAllPermissions() {
    executeQuery("REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + db.getUsername() + "@'%';");
  }

  private void grantCorrectPermissions() {
    executeQuery("GRANT ALTER, CREATE, INSERT, SELECT, DROP ON *.* TO " + db.getUsername() + "@'%';");
  }


  private void executeQuery(final String query) {
    try (final DSLContext dslContext = DSLContextFactory.create(
            "root",
            "test",
            db.getDriverClassName(),
            String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
                    db.getHost(),
                    db.getFirstMappedPort(),
                    db.getDatabaseName()),
            SQLDialect.MYSQL)) {
      new Database(dslContext).query(
              ctx -> ctx
                      .execute(query));
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  protected JsonNode getJsonFromRecord(Record record) {
    return this.getJsonFromRecord(record, (x) -> Optional.empty());
  }

  protected JsonNode getJsonFromRecord(Record record, Function<Object, Optional<String>> valueParser) {
    ObjectNode node = this.mapper.createObjectNode();
    Arrays.stream(record.fields()).forEach((field) -> {
      Object value = record.get(field);
      var parsedValue = valueParser.apply(value);
      if (parsedValue.isPresent()) {
        node.put(field.getName(), parsedValue.get());
      } else {
        switch (field.getDataType().getTypeName()) {
          case "varchar", "nvarchar", "jsonb", "json", "other" -> {
            String stringValue = value != null ? value.toString() : null;
            DestinationAcceptanceTestUtils.putStringIntoJson(stringValue, field.getName(), node);
          }
          default -> node.put(field.getName(), value != null ? value.toString() : null);
        }
      }

    });
    return node;
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    try (final DSLContext dslContext = DSLContextFactory.create(
            db.getUsername(),
            db.getPassword(),
            db.getDriverClassName(),
            String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
                    db.getHost(),
                    db.getFirstMappedPort(),
                    db.getDatabaseName()),
            SQLDialect.MYSQL)) {
      return new Database(dslContext).query(
              ctx -> ctx
                      .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", ObjectUtils.defaultIfNull(schemaName, db.getDatabaseName()), tableName,
                              JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                      .stream()
                      .map(this::getJsonFromRecord)
                      .collect(Collectors.toList()));
    }
  }
}
