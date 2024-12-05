/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor

/** Helper functions to extract [StreamDescriptor] from other POJOs. */
object StreamDescriptorUtils {
    fun fromRecordMessage(msg: AirbyteRecordMessage): StreamDescriptor {
        return StreamDescriptor().withName(msg.stream).withNamespace(msg.namespace)
    }

    fun fromAirbyteStream(stream: AirbyteStream): StreamDescriptor {
        return StreamDescriptor().withName(stream.name).withNamespace(stream.namespace)
    }

    fun fromConfiguredAirbyteSteam(stream: ConfiguredAirbyteStream): StreamDescriptor {
        return fromAirbyteStream(stream.stream)
    }

    fun fromConfiguredCatalog(catalog: ConfiguredAirbyteCatalog): Set<StreamDescriptor> {
        val pairs = HashSet<StreamDescriptor>()

        for (stream in catalog.streams) {
            val pair = fromAirbyteStream(stream.stream)
            pairs.add(pair)
        }

        return pairs
    }

    fun withDefaultNamespace(sd: StreamDescriptor, defaultNamespace: String) =
        if (sd.namespace.isNullOrEmpty()) {
            StreamDescriptor().withName(sd.name).withNamespace(defaultNamespace)
        } else {
            sd
        }
}
