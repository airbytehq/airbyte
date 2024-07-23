/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

import com.google.common.collect.Sets
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode

object RelationalDbReadUtil {
    fun identifyStreamsToSnapshot(
        catalog: ConfiguredAirbyteCatalog,
        alreadySyncedStreams: Set<AirbyteStreamNameNamespacePair>
    ): List<ConfiguredAirbyteStream> {
        val allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog)
        val newlyAddedStreams: Set<AirbyteStreamNameNamespacePair> =
            HashSet(Sets.difference(allStreams, alreadySyncedStreams))
        return catalog.streams
            .filter { c: ConfiguredAirbyteStream -> c.syncMode == SyncMode.INCREMENTAL }
            .filter { stream: ConfiguredAirbyteStream ->
                newlyAddedStreams.contains(
                    AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.stream)
                )
            }
            .map { `object`: ConfiguredAirbyteStream -> Jsons.clone(`object`) }
    }

    @JvmStatic
    fun identifyStreamsForCursorBased(
        catalog: ConfiguredAirbyteCatalog,
        streamsForInitialLoad: List<ConfiguredAirbyteStream>
    ): List<ConfiguredAirbyteStream> {
        val initialLoadStreamsNamespacePairs =
            streamsForInitialLoad
                .map { stream: ConfiguredAirbyteStream ->
                    AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.stream)
                }
                .toSet()
        return catalog.streams
            .filter { c: ConfiguredAirbyteStream -> c.syncMode == SyncMode.INCREMENTAL }
            .filter { stream: ConfiguredAirbyteStream ->
                !initialLoadStreamsNamespacePairs.contains(
                    AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.stream)
                )
            }
            .map { `object`: ConfiguredAirbyteStream -> Jsons.clone(`object`) }
    }

    @JvmStatic
    fun convertNameNamespacePairFromV0(
        v1NameNamespacePair: io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
    ): AirbyteStreamNameNamespacePair {
        return AirbyteStreamNameNamespacePair(
            v1NameNamespacePair.name,
            v1NameNamespacePair.namespace
        )
    }
}
