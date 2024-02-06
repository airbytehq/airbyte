/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.destination.postgres.PostgresDestination;
import io.airbyte.integrations.destination.postgres.PostgresSQLNameTransformer;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class PostgresTypingDedupingTest extends JdbcTypingDedupingTest {

  protected static PostgresTestDatabase testContainer;

  private static final int DEFAULT_VARCHAR_LIMIT_IN_JDBC_GEN = 65535;

  private static final Random RANDOM = new Random();

  private String generateBigString() {
    // Generate exactly 2 chars over the limit
    final int length = DEFAULT_VARCHAR_LIMIT_IN_JDBC_GEN + 2;
    return RANDOM
        .ints('a', 'z' + 1)
        .limit(length)
        .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append)
        .toString();
  }

  @BeforeAll
  public static void setupPostgres() {
    testContainer = PostgresTestDatabase.in(PostgresTestDatabase.BaseImage.POSTGRES_13);
  }

  @AfterAll
  public static void teardownPostgres() {
    testContainer.close();
  }

  @Override
  protected ObjectNode getBaseConfig() {
    final ObjectNode config = (ObjectNode) testContainer.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withResolvedHostAndPort()
        .withCredentials()
        .withoutSsl()
        .build();
    return config.put("use_1s1t_format", true);
  }

  @Override
  protected DataSource getDataSource(final JsonNode config) {
    // Intentionally ignore the config and rebuild it.
    // The config param has the resolved (i.e. in-docker) host/port.
    // We need the unresolved host/port since the test wrapper code is running from the docker host
    // rather than in a container.
    return new PostgresDestination().getDataSource(testContainer.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withHostAndPort()
        .withCredentials()
        .withoutSsl()
        .build());
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres:dev";
  }

  @Override
  protected SqlGenerator<?> getSqlGenerator() {
    return new PostgresSqlGenerator(new PostgresSQLNameTransformer());
  }

  @Override
  protected JdbcCompatibleSourceOperations<?> getSourceOperations() {
    return new PostgresSqlGeneratorIntegrationTest.PostgresSourceOperations();
  }

  @Test
  public void testMixedCasedSchema() throws Exception {
    streamName = "MixedCaseSchema" + streamName;
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1);

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, String streamName) throws Exception {
    return super.dumpRawTableRecords(streamNamespace, streamName.toLowerCase());
  }

  @Test
  public void testVarcharLimitOver64K() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    final AirbyteMessage message = new AirbyteMessage();
    final String largeString = generateBigString();
    final Map<String, Object> data = ImmutableMap.of(
        "id1", 1,
        "id2", 200,
        "updated_at", "2021-01-01T00:00:00Z",
        "name", largeString);
    message.setType(Type.RECORD);
    message.setRecord(new AirbyteRecordMessage()
        .withNamespace(streamNamespace)
        .withStream(streamName)
        .withData(Jsons.jsonNode(data))
        .withEmittedAt(1000L));
    final List<AirbyteMessage> messages1 = new ArrayList<>();
    messages1.add(message);
    runSync(catalog, messages1);

    // Only assert on the large varchar string landing in final table.
    // Rest of the fields' correctness is tested by other means in other tests.
    final List<JsonNode> actualFinalRecords = dumpFinalTableRecords(streamNamespace, streamName);
    assertEquals(1, actualFinalRecords.size());
    assertEquals(largeString, actualFinalRecords.get(0).get("name").asText());

  }

}
