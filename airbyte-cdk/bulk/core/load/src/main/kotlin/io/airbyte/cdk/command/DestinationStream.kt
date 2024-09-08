/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import jakarta.inject.Singleton

/**
 * Internal representation of destination streams. This is intended to be a case class specialized
 * for usability.
 *
 * TODO: Add missing info like sync type, generation_id, etc.
 *
 * TODO: Add dedicated schema type, converted from json-schema.
 */
class DestinationStream(val descriptor: Descriptor) {
    data class Descriptor(val namespace: String, val name: String)

    override fun hashCode(): Int {
        return descriptor.hashCode()
    }

    override fun equals(other: Any?): Boolean {
        return other is DestinationStream && descriptor == other.descriptor
    }

    override fun toString(): String {
        return "DestinationStream(descriptor=$descriptor)"
    }
}

@Singleton
class DestinationStreamFactory {
    fun make(stream: ConfiguredAirbyteStream): DestinationStream {
        return DestinationStream(
            descriptor =
                DestinationStream.Descriptor(
                    namespace = stream.stream.namespace,
                    name = stream.stream.name
                )
        )
    }
}
