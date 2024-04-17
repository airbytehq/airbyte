package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.OrderedColumnInfo;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

public class MssqlInitialLoadFullRefreshGlobalStateManager extends MssqlInitialLoadGlobalStateManager {
    public MssqlInitialLoadFullRefreshGlobalStateManager(final MssqlInitialReadUtil.InitialLoadStreams initialLoadStreams,
                                                         final Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOrderedColInfo,
                                                         final CdcState cdcState,
                                                         final ConfiguredAirbyteCatalog catalog,
                                                         final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
        super(initialLoadStreams, pairToOrderedColInfo, cdcState, catalog, streamStateForIncrementalRunSupplier);
    }

    @Override
    public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
        AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());

        // Full refresh - do not reset status; platform will handle this.
        var ocStatus = getOrderedColumnLoadStatus(pair);
        final List<AirbyteStreamState> streamStates = new ArrayList<>();
        streamStates.add(getAirbyteStreamState(pair, Jsons.jsonNode(ocStatus)));

        final AirbyteGlobalState globalState = new AirbyteGlobalState();
        globalState.setSharedState(Jsons.jsonNode(cdcState));
        globalState.setStreamStates(streamStates); // TODO:check here

        return new AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withGlobal(globalState);
    }
}
