/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Collections;
import java.util.List;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Legacy implementation (pre-per-stream state support) of the {@link StateManager} interface.
 *
 * This implementation assumes that the state matches the {@link DbState} object and effectively
 * tracks state as global across the streams managed by a connector.
 *
 * @deprecated This manager may be removed in the future if/once all connectors support per-stream
 *             state management.
 */
@Deprecated(forRemoval = true)
public class LegacyStateManager extends AbstractStateManager<DbState, DbStreamState> {

  private static final Logger LOGGER = LoggerFactory.getLogger(LegacyStateManager.class);

  /**
   * {@link Function} that extracts the cursor from the stream state.
   */
  private static final Function<DbStreamState, String> CURSOR_FUNCTION = DbStreamState::getCursor;

  /**
   * {@link Function} that extracts the cursor field(s) from the stream state.
   */
  private static final Function<DbStreamState, List<String>> CURSOR_FIELD_FUNCTION = DbStreamState::getCursorField;

  /**
   * {@link Function} that creates an {@link AirbyteStreamNameNamespacePair} from the stream state.
   */
  private static final Function<DbStreamState, AirbyteStreamNameNamespacePair> NAME_NAMESPACE_PAIR_FUNCTION =
      s -> new AirbyteStreamNameNamespacePair(s.getStreamName(), s.getStreamNamespace());

  /**
   * Tracks whether the connector associated with this state manager supports CDC.
   */
  private Boolean isCdc;

  /**
   * {@link CdcStateManager} used to manage state for connectors that support CDC.
   */
  private final CdcStateManager cdcStateManager;

  /**
   * Constructs a new {@link LegacyStateManager} that is seeded with the provided {@link DbState}
   * instance.
   *
   * @param dbState The initial state represented as an {@link DbState} instance.
   * @param catalog The {@link ConfiguredAirbyteCatalog} for the connector associated with this state
   *        manager.
   */
  public LegacyStateManager(final DbState dbState, final ConfiguredAirbyteCatalog catalog) {
    super(catalog,
        () -> dbState.getStreams(),
        CURSOR_FUNCTION,
        CURSOR_FIELD_FUNCTION,
        NAME_NAMESPACE_PAIR_FUNCTION);

    this.cdcStateManager = new CdcStateManager(dbState.getCdcState());
    this.isCdc = dbState.getCdc();
    if (dbState.getCdc() == null) {
      this.isCdc = false;
    }
  }

  @Override
  public CdcStateManager getCdcStateManager() {
    return cdcStateManager;
  }

  @Override
  public AirbyteStateMessage toState() {
    final DbState DbState = new DbState()
        .withCdc(isCdc)
        .withStreams(getPairToCursorInfoMap().entrySet().stream()
            .sorted(Entry.comparingByKey()) // sort by stream name then namespace for sanity.
            .map(e -> new DbStreamState()
                .withStreamName(e.getKey().getName())
                .withStreamNamespace(e.getKey().getNamespace())
                .withCursorField(e.getValue().getCursorField() == null ? Collections.emptyList() : List.of(e.getValue().getCursorField()))
                .withCursor(e.getValue().getCursor()))
            .collect(Collectors.toList()))
        .withCdcState(getCdcStateManager().getCdcState());

    LOGGER.info("Generated legacy state for {} streams");
    return new AirbyteStateMessage().withData(Jsons.jsonNode(DbState));
  }

  @Override
  public AirbyteStateMessage updateAndEmit(final AirbyteStreamNameNamespacePair pair, final String cursor) {
    // cdc file gets updated by debezium so the "update" part is a no op.
    if (!isCdc) {
      final Optional<CursorInfo> cursorInfo = getCursorInfo(pair);
      Preconditions.checkState(cursorInfo.isPresent(), "Could not find cursor information for stream: " + pair);
      cursorInfo.get().setCursor(cursor);
    }

    return toState();
  }

}
