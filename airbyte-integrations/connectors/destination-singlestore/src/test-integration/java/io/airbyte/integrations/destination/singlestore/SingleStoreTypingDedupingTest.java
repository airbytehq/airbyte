/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import static io.airbyte.integrations.base.destination.typing_deduping.StreamId.concatenateRawTableName;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreNamingTransformer;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreSqlGenerator;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.sql.SQLException;
import java.text.MessageFormat;
import java.util.List;
import org.apache.commons.lang3.RandomStringUtils;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class SingleStoreTypingDedupingTest extends BaseTypingDedupingTest {

  private static final String DATABASE = "database_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();
  private static final String DEFAULT_DEV_IMAGE = "airbyte/destination-singlestore:dev";
  private static final JsonNode ALL_TYPES_SCHEMA;

  static {
    try {
      ALL_TYPES_SCHEMA = Jsons.deserialize(MoreResources.readResource("dat/all_types_schema.json"));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected static AirbyteSingleStoreTestContainer db;

  @BeforeAll
  public static void setupDatabase() throws Exception {
    AirbyteSingleStoreTestContainer container = new AirbyteSingleStoreTestContainer();
    container.start();
    final String username = "user_" + RandomStringUtils.randomAlphabetic(5).toLowerCase();
    final String password = RandomStringUtils.randomAlphabetic(10).toLowerCase();
    final String[] sql = new String[] {String.format("CREATE DATABASE %s", DATABASE),
      String.format("CREATE USER %s IDENTIFIED BY '%s'", username, password), String.format("GRANT ALL ON *.* TO %s", username)};
    container.execInContainer("/bin/bash", "-c",
        String.format("set -o errexit -o pipefail; echo \"%s\" | singlestore -v -v -v --user=root --password=root", String.join("; ", sql)));
    db = container.withUsername(username).withPassword(password).withDatabaseName(DATABASE);
  }

  @NotNull
  @Override
  protected String getImageName() {
    return DEFAULT_DEV_IMAGE;
  }

  @Nullable
  @Override
  protected JsonNode generateConfig() throws Exception {
    return io.airbyte.commons.json.Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, DATABASE)
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SSL_KEY, false).build());
  }

  @Override
  protected void teardownStreamAndNamespace(@Nullable String streamNamespace, @NotNull String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema(getConfig());
    }
    getDatabase().execute(String.format("DROP TABLE IF EXISTS %s.%s", getRawSchema(), concatenateRawTableName(streamNamespace, streamName)));
  }

  protected String getDefaultSchema(@NotNull JsonNode config) {
    return config.get("database").asText();
  }

  protected String getRawSchema() {
    return getConfig().get("database").asText();
  }

  @NotNull
  @Override
  protected List<JsonNode> dumpRawTableRecords(@Nullable String streamNamespace, @NotNull String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema(getConfig());
    }
    var tableName = concatenateRawTableName(streamNamespace, Names.toAlphanumericAndUnderscore(streamName));
    var schema = getRawSchema();
    return dumpTable(String.format("%s.%s", schema, tableName));
  }

  private JdbcDatabase getDatabase() {
    var datasource = SingleStoreConnectorFactory.createDataSource(getConfig());
    return new DefaultJdbcDatabase(datasource);
  }

  @NotNull
  @Override
  public List<JsonNode> dumpFinalTableRecords(@Nullable String streamNamespace, @NotNull String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema(getConfig());
    }
    return dumpTable(String.format("%s.%s", streamNamespace, Names.toAlphanumericAndUnderscore(streamName)));
  }

  private List<JsonNode> dumpTable(String tableIdentifier) throws SQLException {
    var sourceOperations =
        new JdbcSourceOperations() {};
    return getDatabase().bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery(MessageFormat.format("SELECT * FROM {0} ORDER BY {1} ASC",
            tableIdentifier, JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)),
        sourceOperations::rowToJson);
  }

  @Test
  public void allTypesData() throws Exception {
    var catalog =
        new io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog()
            .withStreams(
                java.util.List.of(
                    new ConfiguredAirbyteStream()
                        .withSyncMode(SyncMode.INCREMENTAL)
                        .withCursorField(List.of("id2"))
                        .withDestinationSyncMode(DestinationSyncMode.APPEND)
                        .withStream(
                            new AirbyteStream()
                                .withNamespace(getStreamNamespace())
                                .withName(getStreamName())
                                .withJsonSchema(ALL_TYPES_SCHEMA))));

    var messages1 = readMessages("dat/sync1_all_types_messages1.jsonl");

    runSync(catalog, messages1);

    var expectedRawRecords1 = readRecords("dat/sync1_all_types_expectedrecords_raw.jsonl");
    var expectedFinalRecords1 = readRecords("dat/sync1_all_types_expectedrecords_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());
  }

  @NotNull
  @Override
  protected SqlGenerator getSqlGenerator() {
    return new SingleStoreSqlGenerator(new SingleStoreNamingTransformer());
  }

}
