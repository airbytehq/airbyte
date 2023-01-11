/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Factory class that creates {@link StateManager} instances based on the provided state.
 */
public class StateManagerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(StateManagerFactory.class);

  /**
   * Private constructor to prevent direct instantiation.
   */
  private StateManagerFactory() {}

  /**
   * Creates a {@link StateManager} based on the provided state object and catalog. This method will
   * handle the conversion of the provided state to match the requested state manager based on the
   * provided {@link AirbyteStateType}.
   *
   * @param supportedStateType The type of state supported by the connector.
   * @param initialState The deserialized initial state that will be provided to the selected
   *        {@link StateManager}.
   * @param catalog The {@link ConfiguredAirbyteCatalog} for the connector that will utilize the state
   *        manager.
   * @return A newly created {@link StateManager} implementation based on the provided state.
   */
  public static StateManager createStateManager(final AirbyteStateType supportedStateType,
                                                final List<AirbyteStateMessage> initialState,
                                                final ConfiguredAirbyteCatalog catalog) {
    if (initialState != null && !initialState.isEmpty()) {
      final AirbyteStateMessage airbyteStateMessage = initialState.get(0);
      switch (supportedStateType) {
        case LEGACY:
          LOGGER.info("Legacy state manager selected to manage state object with type {}.", airbyteStateMessage.getType());
          return new LegacyStateManager(Jsons.object(airbyteStateMessage.getData(), DbState.class), catalog);
        case GLOBAL:
          LOGGER.info("Global state manager selected to manage state object with type {}.", airbyteStateMessage.getType());
          return new GlobalStateManager(generateGlobalState(airbyteStateMessage), catalog);
        case STREAM:
        default:
          LOGGER.info("Stream state manager selected to manage state object with type {}.", airbyteStateMessage.getType());
          return new StreamStateManager(generateStreamState(initialState), catalog);
      }
    } else {
      throw new IllegalArgumentException("Failed to create state manager due to empty state list.");
    }
  }

  /**
   * Handles the conversion between a different state type and the global state. This method handles
   * the following transitions:
   * <ul>
   * <li>Stream -> Global (not supported, results in {@link IllegalArgumentException}</li>
   * <li>Legacy -> Global (supported)</li>
   * <li>Global -> Global (supported/no conversion required)</li>
   * </ul>
   *
   * @param airbyteStateMessage The current state that is to be converted to global state.
   * @return The converted state message.
   * @throws IllegalArgumentException if unable to convert between the given state type and global.
   */
  private static AirbyteStateMessage generateGlobalState(final AirbyteStateMessage airbyteStateMessage) {
    AirbyteStateMessage globalStateMessage = airbyteStateMessage;

    switch (airbyteStateMessage.getType()) {
      case STREAM:
        throw new IllegalArgumentException("Unable to convert connector state from stream to global.  Please reset the connection to continue.");
      case LEGACY:
        globalStateMessage = StateGeneratorUtils.convertLegacyStateToGlobalState(airbyteStateMessage);
        LOGGER.info("Legacy state converted to global state.", airbyteStateMessage.getType());
        break;
      case GLOBAL:
      default:
        break;
    }

    return globalStateMessage;
  }

  /**
   * Handles the conversion between a different state type and the stream state. This method handles
   * the following transitions:
   * <ul>
   * <li>Global -> Stream (not supported, results in {@link IllegalArgumentException}</li>
   * <li>Legacy -> Stream (supported)</li>
   * <li>Stream -> Stream (supported/no conversion required)</li>
   * </ul>
   *
   * @param states The list of current states.
   * @return The converted state messages.
   * @throws IllegalArgumentException if unable to convert between the given state type and stream.
   */
  private static List<AirbyteStateMessage> generateStreamState(final List<AirbyteStateMessage> states) {
    final AirbyteStateMessage airbyteStateMessage = states.get(0);
    final List<AirbyteStateMessage> streamStates = new ArrayList<>();
    switch (airbyteStateMessage.getType()) {
      case GLOBAL:
        throw new IllegalArgumentException("Unable to convert connector state from global to stream.  Please reset the connection to continue.");
      case LEGACY:
        streamStates.addAll(StateGeneratorUtils.convertLegacyStateToStreamState(airbyteStateMessage));
        break;
      case STREAM:
      default:
        streamStates.addAll(states);
        break;
    }

    return streamStates;
  }

}
