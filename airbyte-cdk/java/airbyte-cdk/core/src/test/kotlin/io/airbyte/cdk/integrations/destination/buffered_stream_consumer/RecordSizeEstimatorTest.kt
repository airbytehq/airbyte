/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class RecordSizeEstimatorTest {
    @Test
    fun testPeriodicSampling() {
        // the estimate performs a size sampling every 3 records
        val sizeEstimator = RecordSizeEstimator(3)
        val stream = "stream"
        val record0 = AirbyteRecordMessage().withStream(stream).withData(DATA_0)
        val record1 = AirbyteRecordMessage().withStream(stream).withData(DATA_1)
        val record2 = AirbyteRecordMessage().withStream(stream).withData(DATA_2)

        // sample record message 1
        val firstEstimation = DATA_1_SIZE
        Assertions.assertEquals(firstEstimation, sizeEstimator.getEstimatedByteSize(record1))
        // next two calls return the first sampling result
        Assertions.assertEquals(firstEstimation, sizeEstimator.getEstimatedByteSize(record0))
        Assertions.assertEquals(firstEstimation, sizeEstimator.getEstimatedByteSize(record0))

        // sample record message 2
        val secondEstimation = firstEstimation / 2 + DATA_2_SIZE / 2
        Assertions.assertEquals(secondEstimation, sizeEstimator.getEstimatedByteSize(record2))
        // next two calls return the second sampling result
        Assertions.assertEquals(secondEstimation, sizeEstimator.getEstimatedByteSize(record0))
        Assertions.assertEquals(secondEstimation, sizeEstimator.getEstimatedByteSize(record0))

        // sample record message 1
        val thirdEstimation = secondEstimation / 2 + DATA_1_SIZE / 2
        Assertions.assertEquals(thirdEstimation, sizeEstimator.getEstimatedByteSize(record1))
        // next two calls return the first sampling result
        Assertions.assertEquals(thirdEstimation, sizeEstimator.getEstimatedByteSize(record0))
        Assertions.assertEquals(thirdEstimation, sizeEstimator.getEstimatedByteSize(record0))
    }

    @Test
    fun testDifferentEstimationPerStream() {
        val sizeEstimator = RecordSizeEstimator()
        val record0 = AirbyteRecordMessage().withStream("stream1").withData(DATA_0)
        val record1 = AirbyteRecordMessage().withStream("stream2").withData(DATA_1)
        val record2 = AirbyteRecordMessage().withStream("stream3").withData(DATA_2)
        Assertions.assertEquals(DATA_0_SIZE, sizeEstimator.getEstimatedByteSize(record0))
        Assertions.assertEquals(DATA_1_SIZE, sizeEstimator.getEstimatedByteSize(record1))
        Assertions.assertEquals(DATA_2_SIZE, sizeEstimator.getEstimatedByteSize(record2))
    }

    companion object {
        private val DATA_0: JsonNode = Jsons.deserialize("{}")
        private val DATA_1: JsonNode = Jsons.deserialize("{ \"field1\": true }")
        private val DATA_2: JsonNode = Jsons.deserialize("{ \"field1\": 10000 }")
        private val DATA_0_SIZE = RecordSizeEstimator.getStringByteSize(DATA_0)
        private val DATA_1_SIZE = RecordSizeEstimator.getStringByteSize(DATA_1)
        private val DATA_2_SIZE = RecordSizeEstimator.getStringByteSize(DATA_2)
    }
}
