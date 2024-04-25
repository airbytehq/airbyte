/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair

class ParsedCatalog(streams: List<StreamConfig>) {
    fun getStream(streamId: AirbyteStreamNameNamespacePair): StreamConfig {
        return getStream(streamId.namespace, streamId.name)
    }

    fun getStream(streamId: StreamId): StreamConfig {
        return getStream(streamId.originalNamespace, streamId.originalName)
    }

    fun getStream(originalNamespace: String?, originalName: String?): StreamConfig {
        return streams
            .stream()
            .filter { s: StreamConfig ->
                s.id.originalNamespace == originalNamespace && s.id.originalName == originalName
            }
            .findFirst()
            .orElseThrow {
                IllegalArgumentException(
                    String.format(
                        "Could not find stream %s.%s out of streams %s",
                        originalNamespace,
                        originalName,
                        streams
                            .stream()
                            .map { stream: StreamConfig ->
                                stream.id.originalNamespace + "." + stream.id.originalName
                            }
                            .toList()
                    )
                )
            }
    }

    val streams: List<StreamConfig>

    init {
        this.streams = streams
    }
}
