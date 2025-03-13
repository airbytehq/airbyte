/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadHandler;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.*;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.*;

class MssqlSourceTest {

  private static final String STREAM_NAME = "id_and_name";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(Lists.newArrayList(CatalogHelpers.createAirbyteStream(
      STREAM_NAME,
      "dbo",
      Field.of("id", JsonSchemaType.INTEGER),
      Field.of("name", JsonSchemaType.STRING),
      Field.of("born", JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE))
      .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
      .withSourceDefinedPrimaryKey(List.of(List.of("id")))
      .withIsResumable(true)));

  private MsSQLTestDatabase testdb;

  private MssqlSource source() {
    return new MssqlSource();
  }

  // how to interact with the mssql test container manaully.
  // 1. exec into mssql container (not the test container container)
  // 2. /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P "A_Str0ng_Required_Password"
  @BeforeEach
  void setup() {
    testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022)
        .with("CREATE TABLE id_and_name(id INTEGER NOT NULL, name VARCHAR(200), born DATETIMEOFFSET(7));")
        .with("INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'),  (2, 'crusher', " +
            "'2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
  }

  @AfterEach
  void cleanUp() {
    testdb.close();
  }

  private JsonNode getConfig() {
    return testdb.testConfigBuilder()
        .withoutSsl()
        .build();
  }

  // if a column in mssql is used as a primary key and in a separate index the discover query returns
  // the column twice. we now de-duplicate it (pr: https://github.com/airbytehq/airbyte/pull/983).
  // this tests that this de-duplication is successful.
  @Test
  void testDiscoverWithPk() {
    testdb
        .with("ALTER TABLE id_and_name ADD CONSTRAINT i3pk PRIMARY KEY CLUSTERED (id);")
        .with("CREATE INDEX i1 ON id_and_name (id);");
    final AirbyteCatalog actual = source().discover(getConfig());
    assertEquals(CATALOG, actual);
  }

  @Test
  void testDiscoverWithoutPk() {
    final AirbyteCatalog actual = source().discover(getConfig());
    assertEquals(STREAM_NAME, actual.getStreams().get(0).getName());
    assertEquals(false, actual.getStreams().get(0).getIsResumable());
  }

  @Test
  @Disabled("See https://github.com/airbytehq/airbyte/pull/23908#issuecomment-1463753684, enable once communication is out")
  public void testTableWithNullCursorValueShouldThrowException() throws Exception {
    testdb
        .with("ALTER TABLE id_and_name ALTER COLUMN id INTEGER NULL")
        .with("INSERT INTO id_and_name(id) VALUES (7), (8), (NULL)");

    ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream().withSyncMode(
        SyncMode.INCREMENTAL)
        .withCursorField(Lists.newArrayList("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withStream(CatalogHelpers.createAirbyteStream(
            STREAM_NAME,
            testdb.getDatabaseName(),
            Field.of("id", JsonSchemaType.INTEGER),
            Field.of("name", JsonSchemaType.STRING),
            Field.of("born", JsonSchemaType.STRING))
            .withSupportedSyncModes(
                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id"))));

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(
        Collections.singletonList(configuredAirbyteStream));

    final Throwable throwable = catchThrowable(() -> MoreIterators.toSet(
        source().read(getConfig(), catalog, null)));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class)
        .hasMessageContaining(
            "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='dbo.id_and_name', cursorColumnName='id', cursorSqlType=INTEGER, cause=Cursor column contains NULL value}");
  }

  @Test
  void testDiscoverWithNonClusteredPk() throws SQLException {
    testdb
        .with("ALTER TABLE id_and_name ADD CONSTRAINT i3pk PRIMARY KEY NONCLUSTERED (id);")
        .with("CREATE INDEX i1 ON id_and_name (id);")
        .with("CREATE CLUSTERED INDEX n1 ON id_and_name (name)");
    final AirbyteCatalog actual = source().discover(getConfig());
    assertEquals(CATALOG, actual);
    final var db = source().createDatabase(getConfig());
    final Map<String, List<String>> oc = MssqlInitialLoadHandler.discoverClusteredIndexForStream(db,
        new AirbyteStream().withName(
            actual.getStreams().get(0).getName()).withNamespace(actual.getStreams().get(0).getNamespace()));

    String firstOcKey = oc.entrySet().iterator().next().getKey();
    List<String> ocValues = oc.get(firstOcKey);
    assertEquals(1, ocValues.size());
    assertEquals("name", ocValues.get(0));
  }

  @Test
  void testDiscoverWithNoClusteredIndex() throws SQLException {
    testdb
        .with("ALTER TABLE id_and_name ADD CONSTRAINT i3pk PRIMARY KEY NONCLUSTERED (id);")
        .with("CREATE INDEX i1 ON id_and_name (id);")
        .with("CREATE NONCLUSTERED INDEX n1 ON id_and_name (name)");
    final AirbyteCatalog actual = source().discover(getConfig());
    assertEquals(CATALOG, actual);
    final var db = source().createDatabase(getConfig());
    final Map<String, List<String>> oc = MssqlInitialLoadHandler.discoverClusteredIndexForStream(db,
        new AirbyteStream().withName(
            actual.getStreams().get(0).getName()).withNamespace(actual.getStreams().get(0).getNamespace()));

    assertNull(oc);
  }

  @Test
  void testDiscoverWithClusteredCompositeIndex() throws SQLException {
    testdb
        .with("ALTER TABLE id_and_name ADD CONSTRAINT i3pk PRIMARY KEY NONCLUSTERED (id);")
        .with("CREATE INDEX i1 ON id_and_name (id);")
        .with("CREATE CLUSTERED INDEX n1 ON id_and_name (id, name)");
    final AirbyteCatalog actual = source().discover(getConfig());
    assertEquals(CATALOG, actual);
    final var db = source().createDatabase(getConfig());

    AirbyteStream stream = new AirbyteStream().withName(
        actual.getStreams().get(0).getName()).withNamespace(actual.getStreams().get(0).getNamespace())
        .withSourceDefinedPrimaryKey(actual.getStreams().get(0).getSourceDefinedPrimaryKey());

    Map<String, List<String>> oc = MssqlInitialLoadHandler.discoverClusteredIndexForStream(db, stream);

    String firstOcKey = oc.entrySet().iterator().next().getKey();
    List<String> ocValues = oc.get(firstOcKey);
    assertEquals(2, ocValues.size());

  }

  @Test
  void testUsingPkWhenClusteredCompositeIndex() throws SQLException {
    testdb
        .with("ALTER TABLE id_and_name ADD CONSTRAINT i3pk PRIMARY KEY NONCLUSTERED (id);")
        .with("CREATE INDEX i1 ON id_and_name (id);")
        .with("CREATE CLUSTERED INDEX n1 ON id_and_name (id, name)");
    final AirbyteCatalog actual = source().discover(getConfig());
    assertEquals(CATALOG, actual);
    final var db = source().createDatabase(getConfig());

    AirbyteStream stream = new AirbyteStream().withName(
        actual.getStreams().getFirst().getName()).withNamespace(actual.getStreams().getFirst().getNamespace())
        .withSourceDefinedPrimaryKey(actual.getStreams().getFirst().getSourceDefinedPrimaryKey());

    ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream().withSyncMode(
        SyncMode.INCREMENTAL)
        .withCursorField(Lists.newArrayList("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withStream(stream);

    final List<List<String>> primaryKey = configuredAirbyteStream.getStream().getSourceDefinedPrimaryKey();
    Optional<String> oc = MssqlInitialReadUtil.selectOcFieldName(db, configuredAirbyteStream);

    assertEquals(primaryKey.getFirst().getFirst(), oc.orElse("No oc"));

  }

  @Test
  void testNonClusteredIndex() throws SQLException {
    testdb
        .with("ALTER TABLE id_and_name ADD CONSTRAINT i3pk PRIMARY KEY NONCLUSTERED (id);")
        .with("CREATE INDEX i1 ON id_and_name (id);");
    final AirbyteCatalog actual = source().discover(getConfig());
    assertEquals(CATALOG, actual);
    final var db = source().createDatabase(getConfig());

    AirbyteStream stream = new AirbyteStream().withName(
        actual.getStreams().getFirst().getName()).withNamespace(actual.getStreams().getFirst().getNamespace())
        .withSourceDefinedPrimaryKey(actual.getStreams().getFirst().getSourceDefinedPrimaryKey());

    ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream().withSyncMode(
        SyncMode.INCREMENTAL)
        .withCursorField(Lists.newArrayList("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withStream(stream);

    Optional<String> oc = MssqlInitialReadUtil.selectOcFieldName(db, configuredAirbyteStream);
    final List<List<String>> primaryKey = configuredAirbyteStream.getStream().getSourceDefinedPrimaryKey();

    assertEquals(primaryKey.getFirst().getFirst(), oc.orElse("No oc"));

  }

  @Test
  void testNonClusteredIndexNoPK() throws SQLException {
    testdb
        .with("ALTER TABLE id_and_name ADD CONSTRAINT i3pk PRIMARY KEY NONCLUSTERED (id);")
        .with("CREATE INDEX i1 ON id_and_name (id);")
        .with("CREATE NONCLUSTERED INDEX n1 ON id_and_name (name)");
    final AirbyteCatalog actual = source().discover(getConfig());
    assertEquals(CATALOG, actual);
    final var db = source().createDatabase(getConfig());

    AirbyteStream stream = new AirbyteStream().withName(
        actual.getStreams().getFirst().getName()).withNamespace(actual.getStreams().getFirst().getNamespace());

    ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream().withSyncMode(
        SyncMode.INCREMENTAL)
        .withCursorField(Lists.newArrayList("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withStream(stream);

    Optional<String> oc = MssqlInitialReadUtil.selectOcFieldName(db, configuredAirbyteStream);

    assert (oc.isEmpty());

  }

}
