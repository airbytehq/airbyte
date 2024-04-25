/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.stream

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteStream

/**
 * Collection of utility methods used to convert objects to [AirbyteStreamNameNamespacePair]
 * objects.
 */
object AirbyteStreamUtils {
    /**
     * Converts an [AirbyteStream] to a [AirbyteStreamNameNamespacePair].
     *
     * @param airbyteStream The [AirbyteStream] to convert.
     * @return The [AirbyteStreamNameNamespacePair].
     */
    fun convertFromAirbyteStream(airbyteStream: AirbyteStream): AirbyteStreamNameNamespacePair {
        return AirbyteStreamNameNamespacePair(airbyteStream.name, airbyteStream.namespace)
    }

    /**
     * Converts a stream name and namespace into a [AirbyteStreamNameNamespacePair].
     *
     * @param name The name of the stream.
     * @param namespace The namespace of the stream.
     * @return The [AirbyteStreamNameNamespacePair].
     */
    @JvmStatic
    fun convertFromNameAndNamespace(
        name: String?,
        namespace: String?
    ): AirbyteStreamNameNamespacePair {
        return AirbyteStreamNameNamespacePair(name, namespace)
    }
}
