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
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.List;
import java.util.Optional;
import java.util.function.Function;
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

    this.cdcStateManager = new CdcStateManager(dbState.getCdcState(), AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog));
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
  public AirbyteStateMessage toState(final Optional<AirbyteStreamNameNamespacePair> pair) {
    final DbState dbState = StateGeneratorUtils.generateDbState(getPairToCursorInfoMap())
        .withCdc(isCdc)
        .withCdcState(getCdcStateManager().getCdcState());

    LOGGER.info("Generated legacy state for {} streams", dbState.getStreams().size());
    return new AirbyteStateMessage().withType(AirbyteStateType.LEGACY).withData(Jsons.jsonNode(dbState));
  }

  @Override
  public AirbyteStateMessage updateAndEmit(final AirbyteStreamNameNamespacePair pair, final String cursor) {
    // cdc file gets updated by debezium so the "update" part is a no op.
    if (!isCdc) {
      final Optional<CursorInfo> cursorInfo = getCursorInfo(pair);
      Preconditions.checkState(cursorInfo.isPresent(), "Could not find cursor information for stream: " + pair);
      cursorInfo.get().setCursor(cursor);
    }

    return toState(Optional.ofNullable(pair));
  }

}
