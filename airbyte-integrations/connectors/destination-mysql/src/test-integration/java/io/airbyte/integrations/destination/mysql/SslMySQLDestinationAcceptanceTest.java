/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class SslMySQLDestinationAcceptanceTest extends MySQLDestinationAcceptanceTest {

  private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);

  private MySQLContainer<?> db;
  private final ExtendedNameTransformer namingResolver = new MySQLNameTransformer();

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("database", db.getDatabaseName())
        .put("port", db.getFirstMappedPort())
        .put("ssl", true)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", "wrong password")
        .put("database", db.getDatabaseName())
        .put("port", db.getFirstMappedPort())
        .put("ssl", false)
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(TestDestinationEnv testEnv, String streamName, String namespace) throws Exception {
    String tableName = namingResolver.getIdentifier(streamName);
    String schema = namingResolver.getIdentifier(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  @Override
  @Test
  public void testCustomDbtTransformations() {
    // We need to create view for testing custom dbt transformations
    executeQuery("GRANT CREATE VIEW ON *.* TO " + db.getUsername() + "@'%';");
    // overrides test with a no-op until https://github.com/dbt-labs/jaffle_shop/pull/8 is merged
    // super.testCustomDbtTransformations();
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
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

  private List<JsonNode> retrieveRecordsFromTable(String tableName, String schemaName) throws SQLException {
    return Databases.createDatabase(
        db.getUsername(),
        db.getPassword(),
        String.format("jdbc:mysql://%s:%s/%s?useSSL=true&requireSSL=true&verifyServerCertificate=false",
            db.getHost(),
            db.getFirstMappedPort(),
            db.getDatabaseName()),
        "com.mysql.cj.jdbc.Driver",
        SQLDialect.MYSQL).query(
            ctx -> ctx
                .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
                    JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                .stream()
                .map(r -> r.formatJSON(JSON_FORMAT))
                .map(Jsons::deserialize)
                .collect(Collectors.toList()));
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

  private void executeQuery(String query) {
    try {
      Databases.createDatabase(
          "root",
          "test",
          String.format("jdbc:mysql://%s:%s/%s?useSSL=true&requireSSL=true&verifyServerCertificate=false",
              db.getHost(),
              db.getFirstMappedPort(),
              db.getDatabaseName()),
          "com.mysql.cj.jdbc.Driver",
          SQLDialect.MYSQL).query(
              ctx -> ctx
                  .execute(query));
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

}
