/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE;
import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE_TIME;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DateTimeUtils;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.TimeZone;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;

// todo (cgardens) - DRY this up with PostgresDestinationAcceptanceTest
public class PostgresDestinationStrictEncryptAcceptanceTest extends DestinationAcceptanceTest {

  private PostgreSQLContainer<?> db;
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres-strict-encrypt:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", "public")
        .put("port", db.getFirstMappedPort())
        .put("database", db.getDatabaseName())
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", "wrong password")
        .put("schema", "public")
        .put("port", db.getFirstMappedPort())
        .put("database", db.getDatabaseName())
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
    // Temporarily disabling the behavior of the ExtendedNameTransformer, see (issue #1785) so we don't
    // use quoted names
    // if (!tableName.startsWith("\"")) {
    // // Currently, Normalization always quote tables identifiers
    // //tableName = "\"" + tableName + "\"";
    // }
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
    return Databases.createPostgresDatabase(db.getUsername(), db.getPassword(),
        db.getJdbcUrl()).query(
            ctx -> ctx
                .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                .stream()
                .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                .map(Jsons::deserialize)
                .collect(Collectors.toList()));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    db = new PostgreSQLContainer<>(DockerImageName.parse("marcosmarxm/postgres-ssl:dev").asCompatibleSubstituteFor("postgres"))
        .withCommand("postgres -c ssl=on -c ssl_cert_file=/var/lib/postgresql/server.crt -c ssl_key_file=/var/lib/postgresql/server.key");
    db.start();
    TimeZone.setDefault(TimeZone.getTimeZone("UTC"));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
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
          case DATE_TIME -> data.put(key.toLowerCase(), DateTimeUtils.convertToPostgresFormat(field.getValue().asText()));
          case DATE -> data.put(key.toLowerCase(), DateTimeUtils.convertToDateFormat(field.getValue().asText()));
        }
      } else {
        data.set(key.toLowerCase(), field.getValue());
      }
    });
  }

}
