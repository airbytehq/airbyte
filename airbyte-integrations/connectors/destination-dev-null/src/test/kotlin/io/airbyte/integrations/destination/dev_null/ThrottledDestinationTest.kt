/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null

import com.google.common.collect.ImmutableMap
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.time.Instant
import java.util.*
import java.util.function.Consumer
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.Mockito.mock

/**
 * This source is designed to be a switch statement for our suite of highly-specific test sources.
 */
class ThrottledDestinationTest {
    @Test
    @Throws(Exception::class)
    fun test() {
        val outputRecordCollector: Consumer<AirbyteMessage> = Mockito.mock()

        val config =
            Jsons.jsonNode(
                Collections.singletonMap(
                    "test_destination",
                    Collections.singletonMap("millis_per_record", 10)
                )
            )

        val consumer = ThrottledDestination().getConsumer(config, mock(), outputRecordCollector)

        consumer.accept(anotherRecord)
        consumer.accept(anotherRecord)
        consumer.accept(anotherRecord)
        consumer.accept(anotherRecord)
        consumer.accept(anotherRecord)
    }

    companion object {
        private val anotherRecord: AirbyteMessage
            get() =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream("data")
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.of(
                                        "column1",
                                        "contents1 " + Instant.now().toEpochMilli()
                                    )
                                )
                            )
                    )
    }
}
