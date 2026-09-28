/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.debezium.engine.ChangeEvent
import java.util.concurrent.atomic.AtomicInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test

/**
 * [ChangeEventWithMetadata] parses the Debezium event lazily and caches the result. The read path
 * touches the value several times per event (op-code check, snapshot metadata, target position, the
 * event converter), and for large change events re-parsing on every read was a significant source
 * of allocation.
 */
internal class ChangeEventWithMetadataTest {

    /** A [ChangeEvent] that counts how many times its key/value are read. */
    private class CountingChangeEvent(
        private val key: String?,
        private val value: String?,
    ) : ChangeEvent<String?, String?> {
        val keyReads = AtomicInteger()
        val valueReads = AtomicInteger()

        override fun key(): String? = key.also { keyReads.incrementAndGet() }

        override fun value(): String? = value.also { valueReads.incrementAndGet() }

        override fun destination(): String = "test-destination"
    }

    @Test
    fun `value is parsed once no matter how many times it is read`() {
        val event =
            CountingChangeEvent(
                key = """{"id":1}""",
                value = """{"op":"u","source":{"snapshot":"false"}}""",
            )
        val subject = ChangeEventWithMetadata(event)

        val first = subject.eventValueAsJson
        repeat(5) { subject.eventValueAsJson }
        // Reached through derived properties as well, which is how the real read path behaves.
        subject.snapshotMetadata
        subject.isSnapshotEvent

        assertEquals(1, event.valueReads.get(), "event value should be deserialized exactly once")
        assertSame(first, subject.eventValueAsJson, "repeated reads should return the cached tree")
        assertEquals("u", subject.eventValueAsJson!!["op"].asText())
    }

    @Test
    fun `key is parsed once no matter how many times it is read`() {
        val event = CountingChangeEvent(key = """{"id":1}""", value = """{"op":"c"}""")
        val subject = ChangeEventWithMetadata(event)

        val first = subject.eventKeyAsJson
        repeat(5) { subject.eventKeyAsJson }

        assertEquals(1, event.keyReads.get(), "event key should be deserialized exactly once")
        assertSame(first, subject.eventKeyAsJson)
        assertEquals(1, subject.eventKeyAsJson!!["id"].asInt())
    }

    @Test
    fun `null key and value stay null and are not re-read`() {
        val event = CountingChangeEvent(key = null, value = null)
        val subject = ChangeEventWithMetadata(event)

        repeat(3) {
            assertNull(subject.eventKeyAsJson)
            assertNull(subject.eventValueAsJson)
        }

        assertEquals(1, event.keyReads.get())
        assertEquals(1, event.valueReads.get())
        assertNull(subject.snapshotMetadata)
    }
}
