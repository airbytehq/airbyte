/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.consumers

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.function.Consumer

/**
 * Default output record collector which serializes the provided {@link AirbyteMessage} as JSON and
 * writes it to standard out.
 */
@Singleton
@Named("outputRecordCollector")
class DefaultOutputRecordCollector : Consumer<AirbyteMessage> {
    override fun accept(airbyteMessage: AirbyteMessage) {
        println(Jsons.serialize(airbyteMessage))
    }
}
