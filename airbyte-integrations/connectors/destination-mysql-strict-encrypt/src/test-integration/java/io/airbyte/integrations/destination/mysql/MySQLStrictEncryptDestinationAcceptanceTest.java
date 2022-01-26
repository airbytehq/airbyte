/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DateTimeUtils;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class MySQLStrictEncryptDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private MySQLContainer<?> db;
  private final ExtendedNameTransformer namingResolver = new MySQLNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mysql-strict-encrypt:dev";
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
  protected boolean supportsNormalization() {
    return true;
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("database", db.getDatabaseName())
        .put("port", db.getFirstMappedPort())
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
        .build());
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get("database") == null) {
      return null;
    }
    return config.get("database").asText();
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
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
                .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                .map(Jsons::deserialize)
                .collect(Collectors.toList()));
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    final String schema = namingResolver.getIdentifier(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
    }
    return result;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    db = new MySQLContainer<>("mysql:8.0");
    db.start();
    setLocalInFileToTrue();
    revokeAllPermissions();
    grantCorrectPermissions();
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
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

  @Override
  @Test
  public void testCustomDbtTransformations() {
    // We need to create view for testing custom dbt transformations
    executeQuery("GRANT CREATE VIEW ON *.* TO " + db.getUsername() + "@'%';");
  }

  @Test
  public void testJsonSync() throws Exception {
    final String catalogAsText = "{\n"
        + "  \"streams\": [\n"
        + "    {\n"
        + "      \"name\": \"exchange_rate\",\n"
        + "      \"json_schema\": {\n"
        + "        \"properties\": {\n"
        + "          \"id\": {\n"
        + "            \"type\": \"integer\"\n"
        + "          },\n"
        + "          \"data\": {\n"
        + "            \"type\": \"string\"\n"
        + "          }"
        + "        }\n"
        + "      }\n"
        + "    }\n"
        + "  ]\n"
        + "}\n";

    final AirbyteCatalog catalog = Jsons.deserialize(catalogAsText, AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = Lists.newArrayList(
        new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(catalog.getStreams().get(0).getName())
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.builder()
                    .put("id", 1)
                    .put("data", "{\"name\":\"Conferência Faturamento - Custo - Taxas - Margem - Resumo ano inicial até -2\",\"description\":null}")
                    .build()))),
        new AirbyteMessage()
            .withType(Type.STATE)
            .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))));

    final JsonNode config = getConfig();
    final String defaultSchema = getDefaultSchema(config);
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);
    retrieveRawRecordsAndAssertSameMessages(catalog, messages, defaultSchema);
  }

  @Override
  @Test
  public void testLineBreakCharacters() {
    // overrides test with a no-op until we handle full UTF-8 in the destination
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
      if (DATE.equals(dateTimeFieldNames.get(key))) {
        data.put(key.toLowerCase(), DateTimeUtils.convertToDateFormat(field.getValue().asText()));
      } else {
        data.set(key.toLowerCase(), field.getValue());
      }
    });
  }

  protected void assertSameValue(final String key, final JsonNode expectedValue, final JsonNode actualValue) {
    if (expectedValue.isBoolean()) {
      // Boolean in MySQL are stored as TINYINT (0 or 1) so we force them to boolean values here
      assertEquals(expectedValue.asBoolean(), actualValue.asBoolean());
    } else {
      assertEquals(expectedValue, actualValue);
    }
  }

}
