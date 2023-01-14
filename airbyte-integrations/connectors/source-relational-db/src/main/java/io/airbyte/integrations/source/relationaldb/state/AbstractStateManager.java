/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.function.Supplier;

/**
 * Abstract implementation of the {@link StateManager} interface that provides common functionality
 * for state manager implementations.
 *
 * @param <T> The type associated with the state object managed by this manager.
 * @param <S> The type associated with the state object stored in the state managed by this manager.
 */
public abstract class AbstractStateManager<T, S> implements StateManager<T, S> {

  /**
   * The {@link CursorManager} responsible for keeping track of the current cursor value for each
   * stream managed by this state manager.
   */
  private final CursorManager cursorManager;

  /**
   * Constructs a new state manager for the given configured connector.
   *
   * @param catalog The connector's configured catalog.
   * @param streamSupplier A {@link Supplier} that provides the cursor manager with the collection of
   *        streams tracked by the connector's state.
   * @param cursorFunction A {@link Function} that extracts the current cursor from a stream stored in
   *        the connector's state.
   * @param cursorFieldFunction A {@link Function} that extracts the cursor field name from a stream
   *        stored in the connector's state.
   * @param cursorRecordCountFunction A {@link Function} that extracts the cursor record count for a
   *        stream stored in the connector's state.
   * @param namespacePairFunction A {@link Function} that generates a
   *        {@link AirbyteStreamNameNamespacePair} that identifies each stream in the connector's
   *        state.
   */
  public AbstractStateManager(final ConfiguredAirbyteCatalog catalog,
                              final Supplier<Collection<S>> streamSupplier,
                              final Function<S, String> cursorFunction,
                              final Function<S, List<String>> cursorFieldFunction,
                              final Function<S, Long> cursorRecordCountFunction,
                              final Function<S, AirbyteStreamNameNamespacePair> namespacePairFunction) {
    cursorManager = new CursorManager(catalog, streamSupplier, cursorFunction, cursorFieldFunction, cursorRecordCountFunction, namespacePairFunction);
  }

  @Override
  public Map<AirbyteStreamNameNamespacePair, CursorInfo> getPairToCursorInfoMap() {
    return cursorManager.getPairToCursorInfo();
  }

  @Override
  public abstract AirbyteStateMessage toState(final Optional<AirbyteStreamNameNamespacePair> pair);

}
