/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/** Helper functions to extract {@link StreamDescriptor} from other POJOs. */
@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class StreamDescriptorUtils {
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
}
