/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlInitialLoadGlobalStateManager extends MySqlInitialLoadStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlInitialLoadGlobalStateManager.class);
  protected StateManager stateManager;

  // Only one global state is emitted, which is fanned out into many entries in the DB by platform. As
  // a result, we need to keep track of streams that
  // have completed the snapshot.
  private Set<AirbyteStreamNameNamespacePair> streamsThatHaveCompletedSnapshot;

  // No special handling for resumable full refresh streams. We will report the cursor as it is.
  private Set<AirbyteStreamNameNamespacePair> resumableFullRefreshStreams;

  // non ResumableFullRefreshStreams do not have any state. We only report count for them.
  private Set<AirbyteStreamNameNamespacePair> nonResumableFullRefreshStreams;
  private Set<AirbyteStreamNameNamespacePair> completedNonResumableFullRefreshStreams;

  private final boolean savedOffsetStillPresentOnServer;
  private final ConfiguredAirbyteCatalog catalog;
  private final CdcState defaultCdcState;

  public MySqlInitialLoadGlobalStateManager(final InitialLoadStreams initialLoadStreams,
                                            final Map<AirbyteStreamNameNamespacePair, PrimaryKeyInfo> pairToPrimaryKeyInfo,
                                            final StateManager stateManager,
                                            final ConfiguredAirbyteCatalog catalog,

                                            final boolean savedOffsetStillPresentOnServer,
                                            final CdcState defaultCdcState) {
    this.stateManager = stateManager;
    this.pairToPrimaryKeyLoadStatus = MySqlInitialLoadStateManager.initPairToPrimaryKeyLoadStatusMap(initialLoadStreams.pairToInitialLoadStatus());
    this.pairToPrimaryKeyInfo = pairToPrimaryKeyInfo;
    this.catalog = catalog;
    this.savedOffsetStillPresentOnServer = savedOffsetStillPresentOnServer;
    this.defaultCdcState = defaultCdcState;
    this.streamStateForIncrementalRunSupplier = pair -> Jsons.emptyObject();
    initStreams(initialLoadStreams, catalog);
  }

  private void initStreams(final InitialLoadStreams initialLoadStreams,
                           final ConfiguredAirbyteCatalog catalog) {
    this.streamsThatHaveCompletedSnapshot = new HashSet<>();
    this.resumableFullRefreshStreams = new HashSet<>();
    this.nonResumableFullRefreshStreams = new HashSet<>();
    this.completedNonResumableFullRefreshStreams = new HashSet<>();

    catalog.getStreams().forEach(configuredAirbyteStream -> {
      var pairInStream =
          new AirbyteStreamNameNamespacePair(configuredAirbyteStream.getStream().getName(), configuredAirbyteStream.getStream().getNamespace());
      if (!initialLoadStreams.streamsForInitialLoad().contains(configuredAirbyteStream)
          && configuredAirbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
        this.streamsThatHaveCompletedSnapshot.add(pairInStream);
      }
      if (configuredAirbyteStream.getSyncMode() == SyncMode.FULL_REFRESH) {
        if (configuredAirbyteStream.getStream().getSourceDefinedPrimaryKey() != null
            && !configuredAirbyteStream.getStream().getSourceDefinedPrimaryKey().isEmpty()) {
          this.resumableFullRefreshStreams.add(pairInStream);
        } else {
          this.nonResumableFullRefreshStreams.add(pairInStream);
        }
      }
    });
  }

  private AirbyteGlobalState generateGlobalState(final List<AirbyteStreamState> streamStates) {
    CdcState cdcState = stateManager.getCdcStateManager().getCdcState();

    if (!savedOffsetStillPresentOnServer || cdcState == null
        || cdcState.getState() == null) {
      cdcState = defaultCdcState;
    }

    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setSharedState(Jsons.jsonNode(cdcState));
    globalState.setStreamStates(streamStates);
    return globalState;
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream airbyteStream) {
    final List<AirbyteStreamState> streamStates = new ArrayList<>();
    streamsThatHaveCompletedSnapshot.forEach(stream -> {
      final DbStreamState state = getFinalState(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(state)));
    });

    resumableFullRefreshStreams.forEach(stream -> {
      var pkStatus = getPrimaryKeyLoadStatus(stream);
      if (pkStatus != null) {
        streamStates.add(getAirbyteStreamState(stream, (Jsons.jsonNode(pkStatus))));
      }
    });

    completedNonResumableFullRefreshStreams.forEach(stream -> {
      streamStates.add(new AirbyteStreamState()
          .withStreamDescriptor(
              new StreamDescriptor().withName(stream.getName()).withNamespace(stream.getNamespace())));
    });

    if (airbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
      AirbyteStreamNameNamespacePair pair =
          new AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());
      var pkStatus = getPrimaryKeyLoadStatus(pair);
      streamStates.add(getAirbyteStreamState(pair, (Jsons.jsonNode(pkStatus))));
    }

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(generateGlobalState(streamStates));
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream airbyteStream) {
    final AirbyteStreamNameNamespacePair pair =
        new AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());
    if (airbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
      streamsThatHaveCompletedSnapshot.add(pair);
    } else if (nonResumableFullRefreshStreams.contains(pair)) {
      completedNonResumableFullRefreshStreams.add(pair);
    }
    final List<AirbyteStreamState> streamStates = new ArrayList<>();

    streamsThatHaveCompletedSnapshot.forEach(stream -> {
      final DbStreamState state = getFinalState(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(state)));
    });

    resumableFullRefreshStreams.forEach(stream -> {
      var pkStatus = getPrimaryKeyLoadStatus(stream);
      streamStates.add(getAirbyteStreamState(stream, (Jsons.jsonNode(pkStatus))));
    });

    completedNonResumableFullRefreshStreams.forEach(stream -> {
      streamStates.add(new AirbyteStreamState()
          .withStreamDescriptor(
              new StreamDescriptor().withName(stream.getName()).withNamespace(stream.getNamespace())));
    });

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(generateGlobalState(streamStates));
  }

  @Override
  public PrimaryKeyInfo getPrimaryKeyInfo(final AirbyteStreamNameNamespacePair pair) {
    return pairToPrimaryKeyInfo.get(pair);
  }

  private AirbyteStreamState getAirbyteStreamState(final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair, final JsonNode stateData) {
    assert Objects.nonNull(pair);
    assert Objects.nonNull(pair.getName());
    assert Objects.nonNull(pair.getNamespace());

    return new AirbyteStreamState()
        .withStreamDescriptor(
            new StreamDescriptor().withName(pair.getName()).withNamespace(pair.getNamespace()))
        .withStreamState(stateData);
  }

  private DbStreamState getFinalState(final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair) {
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
