/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import static io.airbyte.integrations.base.destination.typing_deduping.StreamId.concatenateRawTableName;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.destination.singlestore.typing_deduping.SingleStoreSqlGenerator;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.util.List;
import java.util.Objects;
import javax.sql.DataSource;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;

@Execution(ExecutionMode.SAME_THREAD)
public class SingleStoreTypingDedupingTest extends JdbcTypingDedupingTest {

  private static final String DEFAULT_DEV_IMAGE = "airbyte/destination-singlestore:dev";
  private static final JsonNode ALL_TYPES_SCHEMA;

  static {
    try {
      ALL_TYPES_SCHEMA = Jsons.deserialize(MoreResources.readResource("dat/all_types_schema.json"));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @NotNull
  @Override
  protected String sortColumnKey() {
    return "updated_at";
  }

  protected static SingleStoreTestDatabase db;

  @BeforeAll
  public static void setupDatabase() {
    db = SingleStoreTestDatabase.in(SingleStoreTestDatabase.BaseImage.SINGLESTORE_DEV);
  }

  @AfterAll
  public static void teardownDatabase() {
    db.close();
  }

  @NotNull
  @Override
  protected String generateStreamNamespace() {
    return getBaseConfig().get("database").asText();
  }

  @Nullable
  @Override
  protected JsonNode generateConfig() {
    var config = getBaseConfig();
    setDataSource(getDataSource(config));
    setDatabase(new DefaultJdbcDatabase(Objects.requireNonNull(getDataSource()), getSourceOperations()));
    return config;
  }

  @NotNull
  @Override
  protected String getDefaultSchema(@NotNull JsonNode config) {
    return config.get("database").asText();
  }

  @NotNull
  @Override
  protected String getRawSchema() {
    return getBaseConfig().get("database").asText();
  }

  @NotNull
  @Override
  protected ObjectNode getBaseConfig() {
    return (ObjectNode) db.configBuilder().withDatabase().withResolvedHostAndPort().withCredentials().withoutSsl().build();
  }

  @NotNull
  @Override
  protected SqlGenerator getSqlGenerator() {
    return new SingleStoreSqlGenerator(new SingleStoreNameTransformer(), getConfig());
  }

  @Override
  protected void teardownStreamAndNamespace(@Nullable String streamNamespace, @NotNull String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema(getConfig());
    }
    getDatabase().execute(String.format("DROP TABLE IF EXISTS %s.%s", getRawSchema(), concatenateRawTableName(streamNamespace, streamName)));
  }

  @NotNull
  @Override
  protected List<JsonNode> dumpRawTableRecords(@Nullable String streamNamespace, @NotNull String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema(getConfig());
    }
    var tableName = concatenateRawTableName(streamNamespace, Names.toAlphanumericAndUnderscore(streamName));
    var schema = getRawSchema();
    return getDatabase().queryJsons(String.format("SELECT * FROM %s.%s", schema, tableName));
  }

  @NotNull
  @Override
  public List<JsonNode> dumpFinalTableRecords(@Nullable String streamNamespace, @NotNull String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema(getConfig());
    }
    return getDatabase().queryJsons(String.format("SELECT * FROM %s.%s", streamNamespace, Names.toAlphanumericAndUnderscore(streamName)));
  }

  @Nullable
  @Override
  protected DataSource getDataSource(@Nullable JsonNode config) {
    return new SingleStoreDestination().getDataSource(db.configBuilder().withDatabase().withHostAndPort().withCredentials().withoutSsl().build());
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
  protected String getImageName() {
    return DEFAULT_DEV_IMAGE;
  }

}
