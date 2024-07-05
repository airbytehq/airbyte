/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair

class ParsedCatalog(val streams: List<StreamConfig>) {
    fun getStream(streamId: AirbyteStreamNameNamespacePair): StreamConfig {
        return getStream(streamId.namespace, streamId.name)
    }

    fun getStream(streamId: StreamId): StreamConfig {
        return getStream(streamId.originalNamespace, streamId.originalName)
    }

    fun getStream(originalNamespace: String?, originalName: String?): StreamConfig {
        return streams.firstOrNull { s: StreamConfig ->
            s.id.originalNamespace == originalNamespace && s.id.originalName == originalName
        }
            ?: throw IllegalArgumentException(
                String.format(
                    "Could not find stream %s.%s out of streams %s",
                    originalNamespace,
                    originalName,
                    streams
                        .map { stream: StreamConfig ->
                            stream.id.originalNamespace + "." + stream.id.originalName
                        }
                        .toList()
                )
            )
    }
}
