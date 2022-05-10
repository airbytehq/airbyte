/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.OracleContainer;

class OracleSourceTest {

  private static final String STREAM_NAME = "TEST.ID_AND_NAME";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME,
          Field.of("ID", JsonSchemaType.NUMBER),
          Field.of("NAME", JsonSchemaType.STRING),
          Field.of("IMAGE", JsonSchemaType.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))));
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);
  private static final Set<AirbyteMessage> ASCII_MESSAGES = Sets.newHashSet(createRecord(STREAM_NAME,
      map("ID", new BigDecimal("1.0"), "NAME", "user", "IMAGE", "last_summer.png".getBytes(StandardCharsets.UTF_8))));

  private static OracleContainer ORACLE_DB;

  private static JsonNode config;

  @BeforeAll
  static void init() {
    ORACLE_DB = new OracleContainer("epiclabs/docker-oracle-xe-11g");
    ORACLE_DB.start();
  }

  @BeforeEach
  void setup() throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", ORACLE_DB.getHost())
        .put("port", ORACLE_DB.getFirstMappedPort())
        .put("sid", ORACLE_DB.getSid())
        .put("username", ORACLE_DB.getUsername())
        .put("password", ORACLE_DB.getPassword())
        .put("schemas", List.of("TEST"))
        .build());

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get("username").asText(),
            config.get("password").asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get("host").asText(),
                config.get("port").asInt(),
                config.get("sid").asText())
        )
    );

    database.execute(connection -> {
      connection.createStatement().execute("CREATE USER TEST IDENTIFIED BY TEST DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS");
      connection.createStatement().execute("CREATE TABLE TEST.id_and_name(id NUMERIC(4, 0), name VARCHAR(200), image BLOB)");
      connection.createStatement()
          .execute("INSERT INTO TEST.id_and_name(id, name, image) VALUES (1, 'user', utl_raw.cast_to_raw('last_summer.png'))");
    });

    database.close();
  }

  private JsonNode getConfig(final OracleContainer oracleDb) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", oracleDb.getHost())
        .put("port", oracleDb.getFirstMappedPort())
        .put("sid", oracleDb.getSid())
        .put("username", oracleDb.getUsername())
        .put("password", oracleDb.getPassword())
        .build());
  }

  @AfterAll
  static void cleanUp() {
    ORACLE_DB.close();
  }

  private static void setEmittedAtToNull(final Iterable<AirbyteMessage> messages) {
    for (final AirbyteMessage actualMessage : messages) {
      if (actualMessage.getRecord() != null) {
        actualMessage.getRecord().setEmittedAt(null);
      }
    }
  }

  @Test
  void testReadSuccess() throws Exception {
    final Set<AirbyteMessage> actualMessages = MoreIterators.toSet(new OracleSource().read(config, CONFIGURED_CATALOG, null));
    setEmittedAtToNull(actualMessages);

    assertEquals(ASCII_MESSAGES, actualMessages);
  }

  private static AirbyteMessage createRecord(final String stream, final Map<Object, Object> data) {
    return new AirbyteMessage().withType(Type.RECORD).withRecord(new AirbyteRecordMessage().withData(Jsons.jsonNode(data)).withStream(stream));
  }

  private static Map<Object, Object> map(final Object... entries) {
    if (entries.length % 2 != 0) {
      throw new IllegalArgumentException("Entries must have even length");
    }

    return new HashMap<>() {

      {
        for (int i = 0; i < entries.length; i++) {
          put(entries[i++], entries[i]);
        }
      }

    };
  }

}
