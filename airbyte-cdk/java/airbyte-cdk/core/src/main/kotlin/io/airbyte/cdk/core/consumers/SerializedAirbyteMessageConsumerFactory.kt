/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.consumers

import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import jakarta.inject.Named
import jakarta.inject.Singleton

/**
 * Interface that defines a factory used to create a {@link AirybteMessage} consumer
 * for writing record messages to a destination.
 */
interface SerializedAirbyteMessageConsumerFactory {
    @Throws(Exception::class)
    fun createMessageConsumer(catalog: ConfiguredAirbyteCatalog): SerializedAirbyteMessageConsumer
}

@Singleton
@Named("serializedAirbyteMessageConsumerFactory")
class DefaultSerializedAirbyteMessageConsumerFactory : SerializedAirbyteMessageConsumerFactory {
    override fun createMessageConsumer(catalog: ConfiguredAirbyteCatalog): SerializedAirbyteMessageConsumer {
        return (
            object : SerializedAirbyteMessageConsumer {
                override fun accept(
                    message: String,
                    sizeInBytes: Int,
                ) {}

                override fun close() {}

                override fun start() {}
            }
        )
    }
}
