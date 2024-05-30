/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.createRecord;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.filterRecords;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.map;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.setEmittedAtToNull;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class PostgresSourceSSLTest {

  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("id"))),
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME + "2",
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)),
      CatalogHelpers.createAirbyteStream(
          "names",
          SCHEMA_NAME,
          Field.of("first_name", JsonSchemaType.STRING),
          Field.of("last_name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("first_name"), List.of("last_name")))));
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);
  private static final Set<AirbyteMessage> ASCII_MESSAGES = Sets.newHashSet(
      createRecord(STREAM_NAME, map("id", new BigDecimal("1.0"), "name", "goku", "power", null), SCHEMA_NAME),
      createRecord(STREAM_NAME, map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1), SCHEMA_NAME),
      createRecord(STREAM_NAME, map("id", null, "name", "piccolo", "power", null), SCHEMA_NAME));

  private PostgresTestDatabase testdb;

  @BeforeEach
  void setup() throws Exception {
    testdb = PostgresTestDatabase.in(BaseImage.POSTGRES_SSL_DEV, ContainerModifier.SSL)
        .with("CREATE TABLE id_and_name(id NUMERIC(20, 10) NOT NULL, name VARCHAR(200) NOT NULL, power double precision NOT NULL, PRIMARY KEY (id));")
        .with("CREATE INDEX i1 ON id_and_name (id);")
        .with("INSERT INTO id_and_name (id, name, power) VALUES (1,'goku', 'Infinity'),  (2, 'vegeta', 9000.1), ('NaN', 'piccolo', '-Infinity');")
        .with("CREATE TABLE id_and_name2(id NUMERIC(20, 10) NOT NULL, name VARCHAR(200) NOT NULL, power double precision NOT NULL);")
        .with("INSERT INTO id_and_name2 (id, name, power) VALUES (1,'goku', 'Infinity'),  (2, 'vegeta', 9000.1), ('NaN', 'piccolo', '-Infinity');")
        .with(
            "CREATE TABLE names(first_name VARCHAR(200) NOT NULL, last_name VARCHAR(200) NOT NULL, power double precision NOT NULL, PRIMARY KEY (first_name, last_name));")
        .with(
            "INSERT INTO names (first_name, last_name, power) VALUES ('san', 'goku', 'Infinity'),  ('prince', 'vegeta', 9000.1), ('piccolo', 'junior', '-Infinity');");
  }

  @AfterEach
  void tearDown() {
    testdb.close();
  }

  private JsonNode getConfig() {
    return testdb.testConfigBuilder()
        .withSchemas("public")
        .withSsl(ImmutableMap.builder().put("mode", "require").build())
        .build();
  }

  @Test
  void testDiscoverWithPk() throws Exception {
    final AirbyteCatalog actual = new PostgresSource().discover(getConfig());
    actual.getStreams().forEach(actualStream -> {
      final Optional<AirbyteStream> expectedStream =
          CATALOG.getStreams().stream().filter(stream -> stream.getName().equals(actualStream.getName())).findAny();
      assertTrue(expectedStream.isPresent());
      assertEquals(expectedStream.get(), actualStream);
    });
  }

  @Test
  void testReadSuccess() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_CATALOG.withStreams(CONFIGURED_CATALOG.getStreams().stream().filter(s -> s.getStream().getName().equals(STREAM_NAME))
            .collect(Collectors.toList()));

    final Set<AirbyteMessage> actualMessages = MoreIterators.toSet(new PostgresSource().read(getConfig(), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);

    var actualRecordMessage = filterRecords(actualMessages);
    assertEquals(ASCII_MESSAGES, actualRecordMessage);
  }

  @Test
  void testIsCdc() {
    final JsonNode config = getConfig();

    assertFalse(PostgresUtils.isCdc(config));

    ((ObjectNode) config).set("replication_method", Jsons.jsonNode(ImmutableMap.of(
        "replication_slot", "slot",
        "publication", "ab_pub")));
    assertTrue(PostgresUtils.isCdc(config));
  }

  @Test
  void testAllowSSLWithCdcReplicationMethod() throws Exception {

    JsonNode config = getCDCAndSslModeConfig("allow");

    final AirbyteConnectionStatus actual = new PostgresSource().check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().contains("In CDC replication mode ssl value 'allow' is invalid"));
  }

  @Test
  void testPreferSSLWithCdcReplicationMethod() throws Exception {

    JsonNode config = getCDCAndSslModeConfig("prefer");

    final AirbyteConnectionStatus actual = new PostgresSource().check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().contains("In CDC replication mode ssl value 'prefer' is invalid"));
  }

  private JsonNode getCDCAndSslModeConfig(String sslMode) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.SSL_KEY, true)
        .put(JdbcUtils.SSL_MODE_KEY, Map.of(JdbcUtils.MODE_KEY, sslMode))
        .put("replication_method", Map.of("method", "CDC",
            "replication_slot", "slot",
            "publication", "ab_pub"))
        .build());
  }

}
