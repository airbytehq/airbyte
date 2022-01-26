/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql_strict_encrypt;

import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE;
import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE_TIME;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DateTimeUtils;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.StringUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlStrictEncryptDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static MSSQLServerContainer<?> db;
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();
  private JsonNode config;

  @BeforeAll
  protected static void init() {
    db = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-GA-ubuntu-16.04").acceptLicense();
    db.start();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-mssql-strict-encrypt:dev";
  }

  @Override
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected boolean supportsNormalization() {
    return true;
  }

  private JsonNode getConfig(final MSSQLServerContainer<?> db) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", "test_schema")
        .build());
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", "wrong password")
        .put("schema", "public")
        .put("port", db.getFirstMappedPort())
        .put("ssl", false)
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
    return Databases.createSqlServerDatabase(db.getUsername(), db.getPassword(),
        db.getJdbcUrl()).query(
            ctx -> {
              ctx.fetch(String.format("USE %s;", config.get("database")));
              return ctx
                  .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                  .stream()
                  .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                  .map(Jsons::deserialize)
                  .collect(Collectors.toList());
            });
  }

  private static Database getDatabase(final JsonNode config) {
    return Databases.createSqlServerDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:sqlserver://%s:%s",
            config.get("host").asText(),
            config.get("port").asInt()));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws SQLException {
    final JsonNode configWithoutDbName = getConfig(db);
    final String dbName = Strings.addRandomSuffix("db", "_", 10);

    final Database database = getDatabase(configWithoutDbName);
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
      ctx.fetch(String.format("USE %s;", dbName));
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER NOT NULL, name VARCHAR(200), born DATETIMEOFFSET(7));");
      ctx.fetch("INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'), " +
          " (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
      return null;
    });

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put("database", dbName);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {}

  @AfterAll
  static void cleanUp() {
    db.stop();
    db.close();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = new MssqlStrictEncryptDestination().spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class));
    assertEquals(expected, actual);
  }

  @Override
  public boolean requiresDateTimeConversionForNormalizedSync() {
    return true;
  }

  @Override
  public void convertDateTime(ObjectNode data, Map<String, String> dateTimeFieldNames) {
    var fields = StreamSupport.stream(Spliterators.spliteratorUnknownSize(data.fields(),
        Spliterator.ORDERED), false).toList();
    data.removeAll();
    fields.forEach(field -> {
      var key = field.getKey();
      if (dateTimeFieldNames.containsKey(key)) {
        switch (dateTimeFieldNames.get(key)) {
          case DATE_TIME -> data.put(key.toLowerCase(), DateTimeUtils.convertToMSSQLFormat(field.getValue().asText()));
          case DATE -> data.put(key.toLowerCase(), DateTimeUtils.convertToDateFormat(field.getValue().asText()));
        }
      } else {
        data.set(key.toLowerCase(), field.getValue());
      }
    });
  }

  @Override
  protected void assertSameValue(String key,
      JsonNode expectedValue,
      JsonNode actualValue) {
    if (DATE_TIME.equals(dateTimeFieldNames.getOrDefault(key, StringUtils.EMPTY))) {
      Assertions.assertEquals(DateTimeUtils.MILLISECONDS_PATTERN.matcher(expectedValue.asText()).replaceAll(StringUtils.EMPTY),
          DateTimeUtils.MILLISECONDS_PATTERN.matcher(actualValue.asText()).replaceAll(StringUtils.EMPTY));
    } else {
      super.assertSameValue(key, expectedValue, actualValue);
    }
  }

}
