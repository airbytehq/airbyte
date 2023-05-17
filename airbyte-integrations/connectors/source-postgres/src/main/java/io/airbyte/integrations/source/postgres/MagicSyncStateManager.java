package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.jdbc.iblt.BFEntry;
import io.airbyte.integrations.source.jdbc.iblt.InvertibleBloomFilter;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class to manage MagicSync state.
 */
public class MagicSyncStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(MagicSyncStateManager.class);

  private final Map<AirbyteStreamNameNamespacePair, InvertibleBloomFilter> pairToInvertibleBloomFilter;

  private final static AirbyteStateMessage EMPTY_STATE = new AirbyteStateMessage()
      .withType(AirbyteStateType.STREAM)
      .withStream(new AirbyteStreamState());

  MagicSyncStateManager(final List<AirbyteStateMessage> stateMessages) {
    pairToInvertibleBloomFilter = createPairToMagicSyncStatusMap(stateMessages);
  }

  private static Map<AirbyteStreamNameNamespacePair, InvertibleBloomFilter> createPairToMagicSyncStatusMap(final List<AirbyteStateMessage> stateMessages) {
    final Map<AirbyteStreamNameNamespacePair, InvertibleBloomFilter> localMap = new HashMap<>();
    if (stateMessages != null) {
      for (final AirbyteStateMessage stateMessage : stateMessages) {
        // A reset causes the default state to be an empty legacy state, so we have to ignore those messages.
        if (stateMessage.getType() == AirbyteStateType.STREAM && !stateMessage.equals(EMPTY_STATE)) {
          LOGGER.info("State message: " + stateMessage);
          final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
          final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace());
          final BFEntry[] entries = Jsons.object(stateMessage.getStream().getStreamState(), BFEntry[].class);
          final InvertibleBloomFilter bloomFilter = new InvertibleBloomFilter();
          bloomFilter.addEntries(entries);
          localMap.put(pair, bloomFilter);
        }
      }
    }
    return localMap;
  }

  public InvertibleBloomFilter getInvertibleBloomFilter(final AirbyteStreamNameNamespacePair pair) {
    return pairToInvertibleBloomFilter.get(pair);
  }

  /**
   * Creates AirbyteStateMessage associated with the given {@link MagicSyncStatus}.
   *
   * @return AirbyteMessage which includes information on state of records read so far
   */
  public static AirbyteMessage createStateMessage(final AirbyteStreamNameNamespacePair pair, final InvertibleBloomFilter bloomFilter) {
    final AirbyteStreamState airbyteStreamState =
        new AirbyteStreamState()
            .withStreamDescriptor(
                new StreamDescriptor()
                    .withName(pair.getName())
                    .withNamespace(pair.getNamespace()))
            // Maybe a wrong way of serializing this.
            .withStreamState(new ObjectMapper().valueToTree(bloomFilter.getBFEntrys()));

    // Set state
    final AirbyteStateMessage stateMessage =
        new AirbyteStateMessage()
            .withType(AirbyteStateType.STREAM)
            .withStream(airbyteStreamState);

    LOGGER.info("Creating magsync state: " + stateMessage);
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(stateMessage);
  }
}
