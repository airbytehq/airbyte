/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.function.Executable

internal class StreamIdTest {
    /**
     * Both these streams naively want the same raw table name ("aaa_abab_bbb_abab_ccc"). Verify
     * that they don't actually use the same raw table.
     */
    @Test
    fun rawNameCollision() {
        val stream1 = concatenateRawTableName("aaa_abab_bbb", "ccc")
        val stream2 = concatenateRawTableName("aaa", "bbb_abab_ccc")

        Assertions.assertAll(
            Executable { Assertions.assertEquals("aaa_abab_bbb_raw__stream_ccc", stream1) },
            Executable { Assertions.assertEquals("aaa_raw__stream_bbb_abab_ccc", stream2) }
        )
    }

    @Test
    fun noUnderscores() {
        val stream = concatenateRawTableName("a", "b")

        Assertions.assertEquals("a_raw__stream_b", stream)
    }
}
