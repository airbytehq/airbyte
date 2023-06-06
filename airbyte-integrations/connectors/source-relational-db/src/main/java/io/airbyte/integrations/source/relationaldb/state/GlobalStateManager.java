/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.CURSOR_FIELD_FUNCTION;
import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.CURSOR_FUNCTION;
import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.CURSOR_RECORD_COUNT_FUNCTION;
import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.NAME_NAMESPACE_PAIR_FUNCTION;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Collectors;

/**
 * Global implementation of the {@link StateManager} interface.
 *
 * This implementation generates a single, global state object for the state tracked by this
 * manager.
 */
public class GlobalStateManager extends AbstractStateManager<AirbyteStateMessage, AirbyteStreamState> {

  /**
   * Legacy {@link CdcStateManager} used to manage state for connectors that support Change Data
   * Capture (CDC).
   */
  private final CdcStateManager cdcStateManager;

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
        getStreamsSupplier(airbyteStateMessage),
        CURSOR_FUNCTION,
        CURSOR_FIELD_FUNCTION,
        CURSOR_RECORD_COUNT_FUNCTION,
        NAME_NAMESPACE_PAIR_FUNCTION);

    this.cdcStateManager = new CdcStateManager(extractCdcState(airbyteStateMessage), extractStreams(airbyteStateMessage));
  }

  @Override
  public CdcStateManager getCdcStateManager() {
    return cdcStateManager;
  }

  @Override
  public List<AirbyteStateMessage> getRawStateMessages() {
    throw new UnsupportedOperationException("Raw state retrieval not supported by global state manager.");
  }

  @Override
  public AirbyteStateMessage toState(final Optional<AirbyteStreamNameNamespacePair> pair) {
    // Populate global state
    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setSharedState(Jsons.jsonNode(getCdcStateManager().getCdcState()));
    globalState.setStreamStates(StateGeneratorUtils.generateStreamStateList(getPairToCursorInfoMap()));

    // Generate the legacy state for backwards compatibility
    final DbState dbState = StateGeneratorUtils.generateDbState(getPairToCursorInfoMap())
        .withCdc(true)
        .withCdcState(getCdcStateManager().getCdcState());

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        // Temporarily include legacy state for backwards compatibility with the platform
        .withData(Jsons.jsonNode(dbState))
        .withGlobal(globalState);
  }

  /**
   * Extracts the Change Data Capture (CDC) state stored in the initial state provided to this state
   * manager.
   *
   * @param airbyteStateMessage The {@link AirbyteStateMessage} that contains the initial state
   *        provided to the state manager.
   * @return The {@link CdcState} stored in the state, if any. Note that this will not be {@code null}
   *         but may be empty.
   */
  private CdcState extractCdcState(final AirbyteStateMessage airbyteStateMessage) {
    if (airbyteStateMessage.getType() == AirbyteStateType.GLOBAL) {
      return Jsons.object(airbyteStateMessage.getGlobal().getSharedState(), CdcState.class);
    } else {
      final DbState legacyState = Jsons.object(airbyteStateMessage.getData(), DbState.class);
      return legacyState != null ? legacyState.getCdcState() : null;
    }
  }

  private Set<AirbyteStreamNameNamespacePair> extractStreams(final AirbyteStateMessage airbyteStateMessage) {
    if (airbyteStateMessage.getType() == AirbyteStateType.GLOBAL) {
      return airbyteStateMessage.getGlobal().getStreamStates().stream()
          .map(streamState -> {
            final AirbyteStreamState cloned = Jsons.clone(streamState);
            return new AirbyteStreamNameNamespacePair(cloned.getStreamDescriptor().getName(), cloned.getStreamDescriptor().getNamespace());
          }).collect(Collectors.toSet());
    } else {
      final DbState legacyState = Jsons.object(airbyteStateMessage.getData(), DbState.class);
      return legacyState != null ? extractNamespacePairsFromDbStreamState(legacyState.getStreams()) : Collections.emptySet();
    }
  }

  private Set<AirbyteStreamNameNamespacePair> extractNamespacePairsFromDbStreamState(final List<DbStreamState> streams) {
    return streams.stream().map(stream -> {
      final DbStreamState cloned = Jsons.clone(stream);
      return new AirbyteStreamNameNamespacePair(cloned.getStreamName(), cloned.getStreamNamespace());
    }).collect(Collectors.toSet());
  }

  /**
   * Generates the {@link Supplier} that will be used to extract the streams from the incoming
   * {@link AirbyteStateMessage}.
   *
   * @param airbyteStateMessage The {@link AirbyteStateMessage} supplied to this state manager with
   *        the initial state.
   * @return A {@link Supplier} that will be used to fetch the streams present in the initial state.
   */
  private static Supplier<Collection<AirbyteStreamState>> getStreamsSupplier(final AirbyteStateMessage airbyteStateMessage) {
    /*
     * If the incoming message has the state type set to GLOBAL, it is using the new format. Therefore,
     * we can look for streams in the "global" field of the message. Otherwise, the message is still
     * storing state in the legacy "data" field.
     */
    return () -> {
      if (airbyteStateMessage.getType() == AirbyteStateType.GLOBAL) {
        return airbyteStateMessage.getGlobal().getStreamStates();
      } else if (airbyteStateMessage.getData() != null) {
        return Jsons.object(airbyteStateMessage.getData(), DbState.class).getStreams().stream()
            .map(s -> new AirbyteStreamState().withStreamState(Jsons.jsonNode(s))
                .withStreamDescriptor(new StreamDescriptor().withNamespace(s.getStreamNamespace()).withName(s.getStreamName())))
            .collect(
                Collectors.toList());
      } else {
        return List.of();
      }
    };
  }

}
