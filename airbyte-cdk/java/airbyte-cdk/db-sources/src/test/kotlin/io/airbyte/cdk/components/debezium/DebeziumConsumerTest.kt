/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components.debezium

import io.airbyte.commons.json.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DebeziumConsumerTest {

    @Test
    fun testZero() {
        doTestCase(DebeziumConsumer.Builder(), listOf(), listOf())
    }

    @Test
    fun testMaxRecords() {
        doTestCase(DebeziumConsumer.Builder(maxRecords = 2), listOf(1, 2), listOf(1, 2, 3))
    }

    @Test
    fun testMaxRecordBytes() {
        doTestCase(DebeziumConsumer.Builder(maxRecordBytes = 60), listOf(3, 4), listOf(3, 4, 6))
    }

    fun doTestCase(builder: DebeziumConsumer.Builder, expected: List<Int>, input: List<Int>) {
        val consumer = builder.build()
        for (lsn in input) {
            val json = "{\"lsn\":$lsn,\"source\":{\"snapshot\":\"false\"}}"
            val record = DebeziumRecord(Jsons.deserialize(json))
            consumer.accept(record)
            if (consumer.shouldCheckpoint()) {
                break
            }
        }
        val actual = consumer.flush().map { r -> r.debeziumEventValue["lsn"].asInt() }.toList()
        Assertions.assertIterableEquals(expected, actual, "expected $expected, instead got $actual")
    }
}
