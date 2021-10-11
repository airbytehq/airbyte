/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Handles the state machine for the state of source implementations.
 */
public class StateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(StateManager.class);

  private final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairToCursorInfo;
  private Boolean isCdc;
  private final CdcStateManager cdcStateManager;

  public static DbState emptyState() {
    return new DbState();
  }

  public StateManager(DbState serialized, ConfiguredAirbyteCatalog catalog) {
    this.cdcStateManager = new CdcStateManager(serialized.getCdcState());
    this.isCdc = serialized.getCdc();
    if (serialized.getCdc() == null) {
      this.isCdc = false;
    }

    pairToCursorInfo =
        new ImmutableMap.Builder<AirbyteStreamNameNamespacePair, CursorInfo>().putAll(createCursorInfoMap(serialized, catalog)).build();
  }

  private static Map<AirbyteStreamNameNamespacePair, CursorInfo> createCursorInfoMap(DbState serialized, ConfiguredAirbyteCatalog catalog) {
    final Set<AirbyteStreamNameNamespacePair> allStreamNames = catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStreamNameNamespacePair::fromAirbyteSteam)
        .collect(Collectors.toSet());
    allStreamNames.addAll(serialized.getStreams().stream().map(StateManager::toAirbyteStreamNameNamespacePair).collect(Collectors.toSet()));

    final Map<AirbyteStreamNameNamespacePair, CursorInfo> localMap = new HashMap<>();
    final Map<AirbyteStreamNameNamespacePair, DbStreamState> pairToState = serialized.getStreams()
        .stream()
        .collect(Collectors.toMap(StateManager::toAirbyteStreamNameNamespacePair, a -> a));
    final Map<AirbyteStreamNameNamespacePair, ConfiguredAirbyteStream> pairToConfiguredAirbyteStream = catalog.getStreams().stream()
        .collect(Collectors.toMap(AirbyteStreamNameNamespacePair::fromConfiguredAirbyteSteam, s -> s));

    for (final AirbyteStreamNameNamespacePair pair : allStreamNames) {
      final Optional<DbStreamState> stateOptional = Optional.ofNullable(pairToState.get(pair));
      final Optional<ConfiguredAirbyteStream> streamOptional = Optional.ofNullable(pairToConfiguredAirbyteStream.get(pair));
      localMap.put(pair, createCursorInfoForStream(pair, stateOptional, streamOptional));
    }

    return localMap;
  }

  private static AirbyteStreamNameNamespacePair toAirbyteStreamNameNamespacePair(DbStreamState state) {
    return new AirbyteStreamNameNamespacePair(state.getStreamName(), state.getStreamNamespace());
  }

  @VisibleForTesting
  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  static CursorInfo createCursorInfoForStream(AirbyteStreamNameNamespacePair pair,
                                              Optional<DbStreamState> stateOptional,
                                              Optional<ConfiguredAirbyteStream> streamOptional) {
    final String originalCursorField = stateOptional
        .map(DbStreamState::getCursorField)
        .flatMap(f -> f.size() > 0 ? Optional.of(f.get(0)) : Optional.empty())
        .orElse(null);
    final String originalCursor = stateOptional.map(DbStreamState::getCursor).orElse(null);

    final String cursor;
    final String cursorField;

    // if cursor field is set in catalog.
    if (streamOptional.map(ConfiguredAirbyteStream::getCursorField).isPresent()) {
      cursorField = streamOptional
          .map(ConfiguredAirbyteStream::getCursorField)
          .flatMap(f -> f.size() > 0 ? Optional.of(f.get(0)) : Optional.empty())
          .orElse(null);
      // if cursor field is set in state.
      if (stateOptional.map(DbStreamState::getCursorField).isPresent()) {
        // if cursor field in catalog and state are the same.
        if (stateOptional.map(DbStreamState::getCursorField).equals(streamOptional.map(ConfiguredAirbyteStream::getCursorField))) {
          cursor = stateOptional.map(DbStreamState::getCursor).orElse(null);
          LOGGER.info("Found matching cursor in state. Stream: {}. Cursor Field: {} Value: {}", pair, cursorField, cursor);
          // if cursor field in catalog and state are different.
        } else {
          cursor = null;
          LOGGER.info(
              "Found cursor field. Does not match previous cursor field. Stream: {}. Original Cursor Field: {}. New Cursor Field: {}. Resetting cursor value.",
              pair, originalCursorField, cursorField);
        }
        // if cursor field is not set in state but is set in catalog.
      } else {
        LOGGER.info("No cursor field set in catalog but not present in state. Stream: {}, New Cursor Field: {}. Resetting cursor value", pair,
            cursorField);
        cursor = null;
      }
      // if cursor field is not set in catalog.
    } else {
      LOGGER.info(
          "Cursor field set in state but not present in catalog. Stream: {}. Original Cursor Field: {}. Original value: {}. Resetting cursor.",
          pair, originalCursorField, originalCursor);
      cursorField = null;
      cursor = null;
    }

    return new CursorInfo(originalCursorField, originalCursor, cursorField, cursor);
  }

  private Optional<CursorInfo> getCursorInfo(AirbyteStreamNameNamespacePair pair) {
    return Optional.ofNullable(pairToCursorInfo.get(pair));
  }

  public Optional<String> getOriginalCursorField(AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getOriginalCursorField);
  }

  public Optional<String> getOriginalCursor(AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getOriginalCursor);
  }

  public Optional<String> getCursorField(AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getCursorField);
  }

  public Optional<String> getCursor(AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getCursor);
  }

  synchronized public AirbyteStateMessage updateAndEmit(AirbyteStreamNameNamespacePair pair, String cursor) {
    // cdc file gets updated by debezium so the "update" part is a no op.
    if (!isCdc) {
      final Optional<CursorInfo> cursorInfo = getCursorInfo(pair);
      Preconditions.checkState(cursorInfo.isPresent(), "Could not find cursor information for stream: " + pair);
      cursorInfo.get().setCursor(cursor);
    }

    return toState();
  }

  public void setIsCdc(boolean isCdc) {
    if (this.isCdc == null) {
      this.isCdc = isCdc;
    } else {
      Preconditions.checkState(this.isCdc == isCdc, "attempt to set cdc to {}, but is already set to {}.", isCdc, this.isCdc);
    }
  }

  public CdcStateManager getCdcStateManager() {
    return cdcStateManager;
  }

  public AirbyteStateMessage emit() {
    return toState();
  }

  private AirbyteStateMessage toState() {
    final DbState DbState = new DbState()
        .withCdc(isCdc)
        .withStreams(pairToCursorInfo.entrySet().stream()
            .sorted(Entry.comparingByKey()) // sort by stream name then namespace for sanity.
            .map(e -> new DbStreamState()
                .withStreamName(e.getKey().getName())
                .withStreamNamespace(e.getKey().getNamespace())
                .withCursorField(e.getValue().getCursorField() == null ? Collections.emptyList() : Lists.newArrayList(e.getValue().getCursorField()))
                .withCursor(e.getValue().getCursor()))
            .collect(Collectors.toList()))
        .withCdcState(cdcStateManager.getCdcState());

    return new AirbyteStateMessage().withData(Jsons.jsonNode(DbState));
  }

}
