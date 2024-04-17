package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;

import java.util.Map;
import java.util.function.Function;

public class MssqlInitialLoadFullRefreshStreamStateManager extends MssqlInitialLoadStreamStateManager {
    public MssqlInitialLoadFullRefreshStreamStateManager(final ConfiguredAirbyteCatalog catalog,
                                                         final MssqlInitialReadUtil.InitialLoadStreams initialLoadStreams,
                                                         final Map<AirbyteStreamNameNamespacePair, MssqlInitialReadUtil.OrderedColumnInfo> pairToOrderedColInfo,
                                                         final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
        super(catalog, initialLoadStreams, pairToOrderedColInfo, streamStateForIncrementalRunSupplier);
    }

    @Override
    public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
        AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
        var ocStatus = getOrderedColumnLoadStatus(pair);
        return new AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(getAirbyteStreamState(pair, Jsons.jsonNode(ocStatus)));
    }
}
