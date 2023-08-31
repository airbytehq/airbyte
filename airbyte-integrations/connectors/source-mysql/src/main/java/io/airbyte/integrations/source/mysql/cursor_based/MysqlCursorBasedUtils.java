package io.airbyte.integrations.source.mysql.cursor_based;

import static io.airbyte.integrations.source.mysql.MySqlQueryUtils.getCursorBasedSyncStatusForStreams;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.CURSOR_BASED_STATE_TYPE;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.PRIMARY_KEY_STATE_TYPE;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.STATE_TYPE_KEY;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.identifyStreamsToSnapshot;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.mysql.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class MysqlCursorBasedUtils {

  public static StreamsCategorised categoriseStreams(final JdbcDatabase database,
                                                     final MySqlCursorBasedStateManager stateManager,
                                                     final ConfiguredAirbyteCatalog fullCatalog,
                                                     final String quoteString) {
    final List<AirbyteStateMessage> rawStateMessages = stateManager.getRawStateMessages();
    final Set<AirbyteStreamNameNamespacePair> alreadySeenStreamPairs = new HashSet<>();
    final Set<AirbyteStreamNameNamespacePair> streamsStillInPkSync = new HashSet<>();
    final Set<AirbyteStreamNameNamespacePair> cursorBasedStreamPairs = new HashSet<>();

    // Build a map of stream <-> initial load status for streams that currently have an initial primary
    // key load in progress.
    final Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToInitialLoadStatus = new HashMap<>();
    if (rawStateMessages != null) {
      rawStateMessages.forEach(stateMessage -> {
        final AirbyteStreamState stream = stateMessage.getStream();
        final JsonNode streamState = stream.getStreamState();
        final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }

        final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(),
                                                                                       streamDescriptor.getNamespace());

        // Build a map of stream <-> initial load status for streams that currently have an initial primary
        // key load in progress.

        if (streamState.has(STATE_TYPE_KEY)) {
          if (streamState.get(STATE_TYPE_KEY).asText().equalsIgnoreCase(PRIMARY_KEY_STATE_TYPE)) {
            final PrimaryKeyLoadStatus primaryKeyLoadStatus = Jsons.object(streamState, PrimaryKeyLoadStatus.class);
            pairToInitialLoadStatus.put(pair, primaryKeyLoadStatus);
            streamsStillInPkSync.add(pair);
          } else if (streamState.get(STATE_TYPE_KEY).asText().equalsIgnoreCase(CURSOR_BASED_STATE_TYPE)) {
            cursorBasedStreamPairs.add(pair);
          }
        }
        alreadySeenStreamPairs.add(new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace()));
      });
    }
    final List<ConfiguredAirbyteStream> streamsForPkSync = new ArrayList<>();
    final List<ConfiguredAirbyteStream> streamsForCursorBasedSync = new ArrayList<>();
    fullCatalog.getStreams().stream()
        .filter(stream -> {
          System.out.println(stream.getStream().getSourceDefinedPrimaryKey().toString());
          return streamsStillInPkSync.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream()))
              && streamHasPrimaryKey(stream);
        })
        .map(Jsons::clone)
        .forEach(streamsForPkSync::add);

    fullCatalog.getStreams().stream()
        .filter(stream -> cursorBasedStreamPairs.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream()))).map(Jsons::clone)
        .forEach(streamsForCursorBasedSync::add);
    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyStreamsToSnapshot(fullCatalog, Collections.unmodifiableSet(alreadySeenStreamPairs));
    streamsForPkSync.addAll(newlyAddedStreams);
    final Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> pairToCursorBasedStatus =
        getCursorBasedSyncStatusForStreams(database, streamsForPkSync, stateManager, quoteString);

    return new StreamsCategorised(new InitialLoadStreams(streamsForPkSync, pairToInitialLoadStatus),
                                  new CursorBasedStreams(streamsForCursorBasedSync, pairToCursorBasedStatus));
  }

  private static boolean streamHasPrimaryKey(final ConfiguredAirbyteStream stream) {
    return stream.getStream().getSourceDefinedPrimaryKey().size() > 0;
  }

  public record CursorBasedStreams(List<ConfiguredAirbyteStream> streamsForCursorBased,
                                   Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> pairToCursorBasedStatus) {

  }

  public record StreamsCategorised(InitialLoadStreams initialLoadStreams,
                                   CursorBasedStreams cursorBasedStreams) {

  }

}
