/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Manages the map of streams to current cursor values for state management.
 *
 * @param <S> The type that represents the stream object which holds the current cursor information
 *        in the state.
 */
public class CursorManager<S> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CursorManager.class);

  /**
   * Map of streams (name/namespace tuple) to the current cursor information stored in the state.
   */
  private final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairToCursorInfo;

  /**
   * Constructs a new {@link CursorManager} based on the configured connector and current state
   * information.
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
  public CursorManager(final ConfiguredAirbyteCatalog catalog,
                       final Supplier<Collection<S>> streamSupplier,
                       final Function<S, String> cursorFunction,
                       final Function<S, List<String>> cursorFieldFunction,
                       final Function<S, Long> cursorRecordCountFunction,
                       final Function<S, AirbyteStreamNameNamespacePair> namespacePairFunction,
                       final boolean onlyIncludeIncrementalStreams) {
    pairToCursorInfo = createCursorInfoMap(
        catalog, streamSupplier, cursorFunction, cursorFieldFunction, cursorRecordCountFunction, namespacePairFunction, onlyIncludeIncrementalStreams);
  }

  /**
   * Creates the cursor information map that associates stream name/namespace tuples with the current
   * cursor information for that stream as stored in the connector's state.
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
   * @return A map of streams to current cursor information for the stream.
   */
  @VisibleForTesting
  protected Map<AirbyteStreamNameNamespacePair, CursorInfo> createCursorInfoMap(
                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                final Supplier<Collection<S>> streamSupplier,
                                                                                final Function<S, String> cursorFunction,
                                                                                final Function<S, List<String>> cursorFieldFunction,
                                                                                final Function<S, Long> cursorRecordCountFunction,
                                                                                final Function<S, AirbyteStreamNameNamespacePair> namespacePairFunction,
                                                                                final boolean onlyIncludeIncrementalStreams) {
    final Set<AirbyteStreamNameNamespacePair> allStreamNames = catalog.getStreams()
        .stream()
        .filter(c -> {
          if (onlyIncludeIncrementalStreams) {
            return c.getSyncMode() == SyncMode.INCREMENTAL;
          }
          return true;
        })
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStreamNameNamespacePair::fromAirbyteStream)
        .collect(Collectors.toSet());
    allStreamNames.addAll(streamSupplier.get().stream().map(namespacePairFunction).filter(Objects::nonNull).collect(Collectors.toSet()));

    final Map<AirbyteStreamNameNamespacePair, CursorInfo> localMap = new HashMap<>();
    final Map<AirbyteStreamNameNamespacePair, S> pairToState = streamSupplier.get()
        .stream()
        .collect(Collectors.toMap(namespacePairFunction, Function.identity()));
    final Map<AirbyteStreamNameNamespacePair, ConfiguredAirbyteStream> pairToConfiguredAirbyteStream = catalog.getStreams().stream()
        .collect(Collectors.toMap(AirbyteStreamNameNamespacePair::fromConfiguredAirbyteSteam, Function.identity()));

    for (final AirbyteStreamNameNamespacePair pair : allStreamNames) {
      final Optional<S> stateOptional = Optional.ofNullable(pairToState.get(pair));
      final Optional<ConfiguredAirbyteStream> streamOptional = Optional.ofNullable(pairToConfiguredAirbyteStream.get(pair));
      localMap.put(pair,
          createCursorInfoForStream(pair, stateOptional, streamOptional, cursorFunction, cursorFieldFunction, cursorRecordCountFunction));
    }

    return localMap;
  }

  /**
   * Generates a {@link CursorInfo} object based on the data currently stored in the connector's state
   * for the given stream.
   *
   * @param pair A {@link AirbyteStreamNameNamespacePair} that identifies a specific stream managed by
   *        the connector.
   * @param stateOptional {@link Optional} containing the current state associated with the stream.
   * @param streamOptional {@link Optional} containing the {@link ConfiguredAirbyteStream} associated
   *        with the stream.
   * @param cursorFunction A {@link Function} that provides the current cursor from the state
   *        associated with the stream.
   * @param cursorFieldFunction A {@link Function} that provides the cursor field name for the cursor
   *        stored in the state associated with the stream.
   * @param cursorRecordCountFunction A {@link Function} that extracts the cursor record count for a
   *        stream stored in the connector's state.
   * @return A {@link CursorInfo} object based on the data currently stored in the connector's state
   *         for the given stream.
   */
  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  @VisibleForTesting
  protected CursorInfo createCursorInfoForStream(final AirbyteStreamNameNamespacePair pair,
                                                 final Optional<S> stateOptional,
                                                 final Optional<ConfiguredAirbyteStream> streamOptional,
                                                 final Function<S, String> cursorFunction,
                                                 final Function<S, List<String>> cursorFieldFunction,
                                                 final Function<S, Long> cursorRecordCountFunction) {
    final String originalCursorField = stateOptional
        .map(cursorFieldFunction)
        .flatMap(f -> f.size() > 0 ? Optional.of(f.get(0)) : Optional.empty())
        .orElse(null);
    final String originalCursor = stateOptional.map(cursorFunction).orElse(null);
    final long originalCursorRecordCount = stateOptional.map(cursorRecordCountFunction).orElse(0L);

    final String cursor;
    final String cursorField;
    final long cursorRecordCount;

    // if cursor field is set in catalog.
    if (streamOptional.map(ConfiguredAirbyteStream::getCursorField).isPresent()) {
      cursorField = streamOptional
          .map(ConfiguredAirbyteStream::getCursorField)
          .flatMap(f -> f.size() > 0 ? Optional.of(f.get(0)) : Optional.empty())
          .orElse(null);
      // if cursor field is set in state.
      if (stateOptional.map(cursorFieldFunction).isPresent()) {
        // if cursor field in catalog and state are the same.
        if (stateOptional.map(cursorFieldFunction).equals(streamOptional.map(ConfiguredAirbyteStream::getCursorField))) {
          cursor = stateOptional.map(cursorFunction).orElse(null);
          cursorRecordCount = stateOptional.map(cursorRecordCountFunction).orElse(0L);
          // If a matching cursor is found in the state, and it's value is null - this indicates a CDC stream
          // and we shouldn't log anything.
          if (cursor != null) {
            LOGGER.info("Found matching cursor in state. Stream: {}. Cursor Field: {} Value: {} Count: {}",
                pair, cursorField, cursor, cursorRecordCount);
          }
          // if cursor field in catalog and state are different.
        } else {
          cursor = null;
          cursorRecordCount = 0L;
          LOGGER.info(
              "Found cursor field. Does not match previous cursor field. Stream: {}. Original Cursor Field: {} (count {}). New Cursor Field: {}. Resetting cursor value.",
              pair, originalCursorField, originalCursorRecordCount, cursorField);
        }
        // if cursor field is not set in state but is set in catalog.
      } else {
        LOGGER.info("No cursor field set in catalog but not present in state. Stream: {}, New Cursor Field: {}. Resetting cursor value", pair,
            cursorField);
        cursor = null;
        cursorRecordCount = 0L;
      }
      // if cursor field is not set in catalog.
    } else {
      LOGGER.info(
          "Cursor field set in state but not present in catalog. Stream: {}. Original Cursor Field: {}. Original value: {}. Resetting cursor.",
          pair, originalCursorField, originalCursor);
      cursorField = null;
      cursor = null;
      cursorRecordCount = 0L;
    }

    return new CursorInfo(originalCursorField, originalCursor, originalCursorRecordCount, cursorField, cursor, cursorRecordCount);
  }

  /**
   * Retrieves a copy of the stream name/namespace tuple to current cursor information map.
   *
   * @return A copy of the stream name/namespace tuple to current cursor information map.
   */
  public Map<AirbyteStreamNameNamespacePair, CursorInfo> getPairToCursorInfo() {
    return Map.copyOf(pairToCursorInfo);
  }

  /**
   * Retrieves an {@link Optional} possibly containing the current {@link CursorInfo} associated with
   * the provided stream name/namespace tuple.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} which identifies a stream.
   * @return An {@link Optional} possibly containing the current {@link CursorInfo} associated with
   *         the provided stream name/namespace tuple.
   */
  public Optional<CursorInfo> getCursorInfo(final AirbyteStreamNameNamespacePair pair) {
    return Optional.ofNullable(pairToCursorInfo.get(pair));
  }

  /**
   * Retrieves an {@link Optional} possibly containing the cursor field name associated with the
   * cursor tracked in the state associated with the provided stream name/namespace tuple.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} which identifies a stream.
   * @return An {@link Optional} possibly containing the cursor field name associated with the cursor
   *         tracked in the state associated with the provided stream name/namespace tuple.
   */
  public Optional<String> getCursorField(final AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getCursorField);
  }

  /**
   * Retrieves an {@link Optional} possibly containing the cursor value tracked in the state
   * associated with the provided stream name/namespace tuple.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} which identifies a stream.
   * @return An {@link Optional} possibly containing the cursor value tracked in the state associated
   *         with the provided stream name/namespace tuple.
   */
  public Optional<String> getCursor(final AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getCursor);
  }

}
