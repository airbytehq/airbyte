package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.cdc.PostgresCdcCtidUtils.CtidStreams;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CtidGlobalStateManager extends CtidStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidGlobalStateManager.class);

  private final CdcState cdcState;
  private final Set<AirbyteStreamNameNamespacePair> streamsThatHaveCompletedSnapshot;

  public CtidGlobalStateManager(final CtidStreams ctidStreams,
      final Map<AirbyteStreamNameNamespacePair, Long> fileNodes, final CdcState cdcState, final ConfiguredAirbyteCatalog catalog) {
    super(filterOutExpiredFileNodes(ctidStreams.pairToCtidStatus(), fileNodes));
    this.cdcState = cdcState;
    this.streamsThatHaveCompletedSnapshot = initStreamsCompletedSnapshot(ctidStreams, catalog);
  }

  private static Set<AirbyteStreamNameNamespacePair> initStreamsCompletedSnapshot(final CtidStreams ctidStreams, final ConfiguredAirbyteCatalog catalog) {
    final Set<AirbyteStreamNameNamespacePair> streamsThatHaveCompletedSnapshot = new HashSet<>();
    catalog.getStreams().forEach(configuredAirbyteStream -> {
      if (ctidStreams.streamsForCtidSync().contains(configuredAirbyteStream) || configuredAirbyteStream.getSyncMode() != SyncMode.INCREMENTAL) {
        return;
      }
      streamsThatHaveCompletedSnapshot.add(
          new AirbyteStreamNameNamespacePair(configuredAirbyteStream.getStream().getName(), configuredAirbyteStream.getStream().getNamespace()));
    });
    return streamsThatHaveCompletedSnapshot;
  }

  private static Map<AirbyteStreamNameNamespacePair, CtidStatus> filterOutExpiredFileNodes(
      final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus,
      final Map<AirbyteStreamNameNamespacePair, Long> fileNodes) {
    final Map<AirbyteStreamNameNamespacePair, CtidStatus> filteredMap = new HashMap<>();
    pairToCtidStatus.forEach((pair, ctidStatus) -> {
      final AirbyteStreamNameNamespacePair updatedPair = new AirbyteStreamNameNamespacePair(pair.getName(), pair.getNamespace());
      if (validateRelationFileNode(ctidStatus, updatedPair, fileNodes)) {
        filteredMap.put(updatedPair, ctidStatus);
      } else {
        LOGGER.warn(
            "The relation file node for table in source db {} is not equal to the saved ctid state, a full sync from scratch will be triggered.",
            pair);
      }
    });
    return filteredMap;
  }

  @Override
  public AirbyteStateMessage createCtidStateMessage(final AirbyteStreamNameNamespacePair pair, final CtidStatus ctidStatus) {
    final List<AirbyteStreamState> streamStates = new ArrayList<>();
    streamsThatHaveCompletedSnapshot.forEach(stream -> {
      final DbStreamState state = getFinalState(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(state)));

    });
    streamStates.add(getAirbyteStreamState(pair, (Jsons.jsonNode(ctidStatus))));
    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setSharedState(Jsons.jsonNode(cdcState));
    globalState.setStreamStates(streamStates);

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(globalState);
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun) {
    streamsThatHaveCompletedSnapshot.add(pair);
    final List<AirbyteStreamState> streamStates = new ArrayList<>();
    streamsThatHaveCompletedSnapshot.forEach(stream -> {
      final DbStreamState state = getFinalState(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(state)));
    });

    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setSharedState(Jsons.jsonNode(cdcState));
    globalState.setStreamStates(streamStates);

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(globalState);
  }

  private AirbyteStreamState getAirbyteStreamState(final AirbyteStreamNameNamespacePair pair, final JsonNode stateData) {
    assert Objects.nonNull(pair);
    assert Objects.nonNull(pair.getName());
    assert Objects.nonNull(pair.getNamespace());

    return new AirbyteStreamState()
        .withStreamDescriptor(
            new StreamDescriptor().withName(pair.getName()).withNamespace(pair.getNamespace()))
        .withStreamState(stateData);
  }

  private DbStreamState getFinalState(final AirbyteStreamNameNamespacePair pair) {
    assert Objects.nonNull(pair);
    assert Objects.nonNull(pair.getName());
    assert Objects.nonNull(pair.getNamespace());

    return new DbStreamState()
        .withStreamName(pair.getName())
        .withStreamNamespace(pair.getNamespace())
        .withCursorField(Collections.emptyList())
        .withCursor(null);
  }
}
