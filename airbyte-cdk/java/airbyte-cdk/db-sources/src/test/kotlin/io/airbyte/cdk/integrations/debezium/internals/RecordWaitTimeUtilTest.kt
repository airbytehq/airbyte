/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.airbyte.commons.json.Jsons
import java.time.Duration
import java.util.*
import java.util.Map
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class RecordWaitTimeUtilTest {
    @Test
    fun testGetFirstRecordWaitTime() {
        val emptyConfig = Jsons.jsonNode(emptyMap<Any, Any>())
        Assertions.assertDoesNotThrow { RecordWaitTimeUtil.checkFirstRecordWaitTime(emptyConfig) }
        Assertions.assertEquals(
            Optional.empty<Any>(),
            RecordWaitTimeUtil.getFirstRecordWaitSeconds(emptyConfig)
        )
        Assertions.assertEquals(
            RecordWaitTimeUtil.DEFAULT_FIRST_RECORD_WAIT_TIME,
            RecordWaitTimeUtil.getFirstRecordWaitTime(emptyConfig)
        )

        val normalConfig =
            Jsons.jsonNode(
                Map.of(
                    "replication_method",
                    Map.of("method", "CDC", "initial_waiting_seconds", 500)
                )
            )
        Assertions.assertDoesNotThrow { RecordWaitTimeUtil.checkFirstRecordWaitTime(normalConfig) }
        Assertions.assertEquals(
            Optional.of(500),
            RecordWaitTimeUtil.getFirstRecordWaitSeconds(normalConfig)
        )
        Assertions.assertEquals(
            Duration.ofSeconds(500),
            RecordWaitTimeUtil.getFirstRecordWaitTime(normalConfig)
        )

        val tooShortTimeout = RecordWaitTimeUtil.MIN_FIRST_RECORD_WAIT_TIME.seconds.toInt() - 1
        val tooShortConfig =
            Jsons.jsonNode(
                Map.of(
                    "replication_method",
                    Map.of("method", "CDC", "initial_waiting_seconds", tooShortTimeout)
                )
            )
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            RecordWaitTimeUtil.checkFirstRecordWaitTime(tooShortConfig)
        }
        Assertions.assertEquals(
            Optional.of(tooShortTimeout),
            RecordWaitTimeUtil.getFirstRecordWaitSeconds(tooShortConfig)
        )
        Assertions.assertEquals(
            RecordWaitTimeUtil.MIN_FIRST_RECORD_WAIT_TIME,
            RecordWaitTimeUtil.getFirstRecordWaitTime(tooShortConfig)
        )

        val tooLongTimeout = RecordWaitTimeUtil.MAX_FIRST_RECORD_WAIT_TIME.seconds.toInt() + 1
        val tooLongConfig =
            Jsons.jsonNode(
                Map.of(
                    "replication_method",
                    Map.of("method", "CDC", "initial_waiting_seconds", tooLongTimeout)
                )
            )
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            RecordWaitTimeUtil.checkFirstRecordWaitTime(tooLongConfig)
        }
        Assertions.assertEquals(
            Optional.of(tooLongTimeout),
            RecordWaitTimeUtil.getFirstRecordWaitSeconds(tooLongConfig)
        )
        Assertions.assertEquals(
            RecordWaitTimeUtil.MAX_FIRST_RECORD_WAIT_TIME,
            RecordWaitTimeUtil.getFirstRecordWaitTime(tooLongConfig)
        )
    }
}
