package io.airbyte.integrations.source.relationaldb.state;

import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR_FIELD1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR_FIELD2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAMESPACE;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAME_NAMESPACE_PAIR1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAME_NAMESPACE_PAIR2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.STREAM_NAME1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.STREAM_NAME2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.STREAM_NAME3;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link LegacyAdapterStateManagerTest} class.
 */
public class LegacyAdapterStateManagerTest {

  @Test
  void testToState() {
    // TODO update to include state type once available
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE))
                .withCursorField(List.of(CURSOR_FIELD2)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME3).withNamespace(NAMESPACE))));

    final StateManager stateManager = new LegacyAdapterStateManager(new DbState(), catalog);

    final AirbyteStateMessage expectedFirstEmission = new AirbyteStateMessage()
        .withData(Jsons.jsonNode(new DbState().withStreams(List.of(
                    new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD1))
                        .withCursor("a"),
                    new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD2)),
                    new DbStreamState().withStreamName(STREAM_NAME3).withStreamNamespace(NAMESPACE))
                .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()))
            .withCdc(false)));
    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a");
    assertEquals(expectedFirstEmission, actualFirstEmission);
    final AirbyteStateMessage expectedSecondEmission = new AirbyteStateMessage()
        .withData(Jsons.jsonNode(new DbState().withStreams(List.of(
                    new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD1))
                        .withCursor("a"),
                    new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD2))
                        .withCursor("b"),
                    new DbStreamState().withStreamName(STREAM_NAME3).withStreamNamespace(NAMESPACE))
                .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()))
            .withCdc(false)));
    final AirbyteStateMessage actualSecondEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR2, "b");
    assertEquals(expectedSecondEmission, actualSecondEmission);
  }
}
