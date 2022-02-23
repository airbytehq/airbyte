/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.testcontainers.containers.PostgreSQLContainer;

public class JdbcDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private PostgreSQLContainer<?> db;
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-jdbc:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", "public")
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            db.getHost(),
            db.getFirstMappedPort(),
            db.getDatabaseName()))
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", db.getUsername())
        .put("password", "wrong password")
        .put("schema", "public")
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            db.getHost(),
            db.getFirstMappedPort(),
            db.getDatabaseName()))
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namingResolver.getIdentifier(namespace))
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
      throws Exception {
    String tableName = namingResolver.getIdentifier(streamName);
    if (!tableName.startsWith("\"")) {
      // Currently, Normalization always quote tables identifiers
      tableName = "\"" + tableName + "\"";
    }
    return retrieveRecordsFromTable(tableName, namingResolver.getIdentifier(namespace));
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

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schema) throws SQLException {
    return Databases.createPostgresDatabase(db.getUsername(), db.getPassword(),
        db.getJdbcUrl()).query(
            ctx -> ctx
                .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schema, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                .stream()
                .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                .map(Jsons::deserialize)
                .collect(Collectors.toList()));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    db = new PostgreSQLContainer<>("postgres:13-alpine");
    db.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

}
