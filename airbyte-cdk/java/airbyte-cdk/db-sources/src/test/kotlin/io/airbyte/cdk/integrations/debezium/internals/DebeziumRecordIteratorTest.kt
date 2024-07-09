/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition
import io.debezium.engine.ChangeEvent
import java.time.Duration
import java.util.*
import org.apache.kafka.connect.source.SourceRecord
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock

class DebeziumRecordIteratorTest {
    @Test
    fun getHeartbeatPositionTest() {
        val debeziumRecordIterator =
            DebeziumRecordIterator(
                mock(),
                object : CdcTargetPosition<Long> {
                    override fun reachedTargetPosition(
                        changeEventWithMetadata: ChangeEventWithMetadata?
                    ): Boolean {
                        return false
                    }

                    override fun extractPositionFromHeartbeatOffset(
                        sourceOffset: Map<String?, *>
                    ): Long {
                        return sourceOffset["lsn"] as Long
                    }
                },
                { false },
                mock(),
                Duration.ZERO,
                getTestConfig(), // Heartbeats should not be ignored for tests.
            )
        val lsn =
            debeziumRecordIterator.getHeartbeatPosition(
                object : ChangeEvent<String?, String?> {
                    private val sourceRecord =
                        SourceRecord(
                            null,
                            Collections.singletonMap("lsn", 358824993496L),
                            null,
                            null,
                            null,
                        )

                    override fun key(): String? {
                        return null
                    }

                    override fun value(): String {
                        return "{\"ts_ms\":1667616934701}"
                    }

                    override fun destination(): String? {
                        return null
                    }

                    fun sourceRecord(): SourceRecord {
                        return sourceRecord
                    }
                },
            )

        Assertions.assertEquals(lsn, 358824993496L)
    }

    fun getTestConfig(): JsonNode {
        val mapper: ObjectMapper = ObjectMapper()
        val testConfig = "{\"is_test\": true}"
        return mapper.readTree(testConfig)
    }
}
