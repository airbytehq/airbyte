package io.airbyte.integrations.source.relationaldb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.AbstractDatabase;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaType;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link AbstractDbSource} class.
 */
public class AbstractDbSourceTest {

  @Test
  void testDeserializationOfState() throws IOException {
    final AbstractDbSource dbSource = new TestAbstractDbSource();
    final JsonNode config = mock(JsonNode.class);

    final String globalStateJson = MoreResources.readResource("states/global.json");
    final String legacyStateJson = MoreResources.readResource("states/legacy.json");
    final String streamStateJson = MoreResources.readResource("states/per_stream.json");

    final JsonNode globalState = Jsons.deserialize(globalStateJson);
    final JsonNode legacyState = Jsons.deserialize(legacyStateJson);
    final JsonNode streamState = Jsons.deserialize(streamStateJson);

    // Legacy state
    final List<AirbyteStateMessage> result1 = dbSource.deserializeInitialState(legacyState, config);
    assertEquals(1, result1.size());
    assertEquals(AirbyteStateType.LEGACY, result1.get(0).getType());

    // Global state
    final List<AirbyteStateMessage> result2 = dbSource.deserializeInitialState(globalState, config);
    assertEquals(1, result2.size());
    assertEquals(AirbyteStateType.GLOBAL, result2.get(0).getType());

    // Per-stream state
    final List<AirbyteStateMessage> result3 = dbSource.deserializeInitialState(streamState, config);
    assertEquals(2, result3.size());
    assertEquals(AirbyteStateType.STREAM, result3.get(0).getType());

    // Null/empty state
    final List<AirbyteStateMessage> result4 = dbSource.deserializeInitialState(null, config);
    assertEquals(1, result4.size());
    assertEquals(dbSource.getSupportedStateType(config), result4.get(0).getType());
  }

  private static class TestAbstractDbSource extends AbstractDbSource {

    @Override
    public JsonNode toDatabaseConfig(final JsonNode config) {
      return null;
    }

    @Override
    protected AbstractDatabase createDatabase(final JsonNode config) throws Exception {
      return null;
    }

    @Override
    public List<CheckedConsumer> getCheckOperations(final JsonNode config) throws Exception {
      return null;
    }

    @Override
    protected JsonSchemaType getType(final Object columnType) {
      return null;
    }

    @Override
    public Set<String> getExcludedInternalNameSpaces() {
      return null;
    }

    @Override
    protected List<TableInfo<CommonField>> discoverInternal(final AbstractDatabase database) throws Exception {
      return null;
    }

    @Override
    protected List<TableInfo<CommonField>> discoverInternal(final AbstractDatabase database, final String schema) throws Exception {
      return null;
    }

    @Override
    protected String getQuoteString() {
      return null;
    }

    @Override
    public AutoCloseableIterator<JsonNode> queryTableIncremental(final AbstractDatabase database, final List columnNames, final String schemaName, final String tableName,
        final String cursorField, final Object cursorFieldType, final String cursor) {
      return null;
    }

    @Override
    public AutoCloseableIterator<JsonNode> queryTableFullRefresh(final AbstractDatabase database, final List columnNames, final String schemaName,
        final String tableName) {
      return null;
    }

    @Override
    protected Map<String, List<String>> discoverPrimaryKeys(final AbstractDatabase database, final List list) {
      return null;
    }

    @Override
    public void close() throws Exception {

    }
  }
}
