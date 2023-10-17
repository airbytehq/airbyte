/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import static io.airbyte.cdk.db.jdbc.JdbcUtils.DATABASE_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import org.junit.jupiter.api.Test;

public class RelationalDbDebeziumPropertiesManagerTest {

  private static final String DATABASE_NAME = "test_database";
  private static final Path PATH = Path.of(".");
  public static final String EXPECTED_CONNECTION_STRING = "mongodb://localhost:27017/?retryWrites=false&provider=airbyte&tls=true";

  @Test
  void testDatabaseName() {
    final List<ConfiguredAirbyteStream> streams = createStreams(4);
    final AirbyteFileOffsetBackingStore offsetManager = mock(AirbyteFileOffsetBackingStore.class);
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final JsonNode invalidConfig = createConfiguration("in-valid_k@invalid234~");

    when(offsetManager.getOffsetFilePath()).thenReturn(PATH);
    when(catalog.getStreams()).thenReturn(streams);

    final Properties cdcProperties = new Properties();
    cdcProperties.put("test", "value");

    RelationalDbDebeziumPropertiesManager relationalDbDebeziumPropertiesManager = new RelationalDbDebeziumPropertiesManager(
        cdcProperties,
        invalidConfig,
        catalog,
        offsetManager,
        Optional.empty());

    // Invalid database name should be modified.
    assertEquals(relationalDbDebeziumPropertiesManager.getName(invalidConfig), "in-valid_kinvalid234");

    // Valid database name should NOT be modified.
    final String validDbName = "valid123_db-name";
    final JsonNode validConfig = createConfiguration(validDbName);
    relationalDbDebeziumPropertiesManager = new RelationalDbDebeziumPropertiesManager(
        cdcProperties,
        validConfig,
        catalog,
        offsetManager,
        Optional.empty());
    assertEquals(relationalDbDebeziumPropertiesManager.getName(validConfig), validDbName);
  }

  private JsonNode createConfiguration(final String dbName) {
    final Map<String, Object> baseConfig = Map.of(DATABASE_KEY, dbName);
    final Map<String, Object> config = new HashMap<>(baseConfig);
    return Jsons.deserialize(Jsons.serialize(config));
  }

  private List<ConfiguredAirbyteStream> createStreams(final int numberOfStreams) {
    final List<ConfiguredAirbyteStream> streams = new ArrayList<>();
    for (int i = 0; i < numberOfStreams; i++) {
      final AirbyteStream stream = new AirbyteStream().withNamespace(DATABASE_NAME).withName("collection" + i);
      streams.add(new ConfiguredAirbyteStream().withStream(stream));
    }
    return streams;
  }

}
