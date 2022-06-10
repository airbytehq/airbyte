package io.airbyte.integrations.source.relationaldb.state;

import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.CURSOR_FIELD_FUNCTION;
import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.CURSOR_FUNCTION;
import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.NAME_NAMESPACE_PAIR_FUNCTION;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;

/**
 * Global implementation of the {@link StateManager} interface.
 *
 * This implementation generates a single, global state object for the state
 * tracked by this manager.
 */
public class GlobalStateManager extends AbstractStateManager<AirbyteStateMessage, AirbyteStreamState> {

  /**
   * Constructs a new {@link GlobalStateManager} that is seeded with the provided
   * {@link AirbyteStateMessage}.
   *
   * @param airbyteStateMessage The initial state represented as an {@link AirbyteStateMessage}.
   * @param catalog The {@link ConfiguredAirbyteCatalog} for the connector associated with this state
   *        manager.
   */
  public GlobalStateManager(final AirbyteStateMessage airbyteStateMessage, final ConfiguredAirbyteCatalog catalog) {
    super(catalog,
        () -> airbyteStateMessage.getStreams(),
        CURSOR_FUNCTION,
        CURSOR_FIELD_FUNCTION,
        NAME_NAMESPACE_PAIR_FUNCTION);
  }

  @Override
  public CdcStateManager getCdcStateManager() {
    return null;
  }

  @Override
  public AirbyteStateMessage toState() {
      final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairToCursorInfoMap = getPairToCursorInfoMap();
      final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage();
      return airbyteStateMessage
          .withStateType(AirbyteStateType.GLOBAL)
          // Temporarily include legacy state for backwards compatibility with the platform
          .withData(Jsons.jsonNode(StateGeneratorUtils.generateDbState(pairToCursorInfoMap)))
          // TODO generate global state
          .withGlobal(null);
    }
}
