/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.copy

import java.util.UUID
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class S3CopyPathsTest {
    private val zero = UUID(0, 0)
    private val config =
        S3CopyConfiguration(
            "role",
            "bucket",
            "region",
            UUID(0, 4),
            UUID(0, 2),
            UUID(0, 3),
            "fusion",
            null,
            UUID(0, 1),
            UUID(0, 5)
        )
    private val epochSeconds = 1789400000L

    @Test
    fun `run paths include all five IDs epoch and escaped original stream`() {
        val path = S3CopyPaths.run(config, "Orders/日本 %", zero, epochSeconds)
        assertEquals(
            "fusion/organizations/${config.organizationId}/workspaces/${config.workspaceId}/sources/${config.sourceId}/connections/${config.connectionId}/destinations/${config.destinationId}/syncs/runs/$epochSeconds/$zero/streams/Orders%2F%E6%97%A5%E6%9C%AC%20%25/",
            path,
        )
        assertEquals(path, S3CopyPaths.run(config, "Orders/日本 %", zero, epochSeconds))
        assertNotEquals(path, S3CopyPaths.run(config, "Orders/日本 %", UUID(0, 1), epochSeconds))
        assertNotEquals(path, S3CopyPaths.run(config, "Orders/日本 %", zero, epochSeconds + 1))
        listOf(
                config.copy(organizationId = zero),
                config.copy(workspaceId = zero),
                config.copy(sourceId = zero),
                config.copy(connectionId = zero),
                config.copy(destinationId = zero),
            )
            .forEach { other ->
                assertNotEquals(path, S3CopyPaths.run(other, "Orders/日本 %", zero, epochSeconds))
            }
        assertNotEquals(path, S3CopyPaths.run(config, "orders/日本 %", zero, epochSeconds))
    }

    @Test
    fun `encoding cannot confuse literal percent escapes or relative segments`() {
        assertEquals("a%2Fb", S3CopyPaths.escape("a/b"))
        assertEquals("a%252Fb", S3CopyPaths.escape("a%2Fb"))
        assertEquals("%2E", S3CopyPaths.escape("."))
        assertEquals("%2E%2E", S3CopyPaths.escape(".."))
        assertEquals("Orders.v1-_~", S3CopyPaths.escape("Orders.v1-_~"))
        assertThrows(IllegalArgumentException::class.java) { S3CopyPaths.escape("") }
    }

    @Test
    fun `key byte limit reserves full batch suffix and accepts exactly 1024 bytes`() {
        val suffix = "batches/$zero.csv.gz"
        val base = S3CopyPaths.run(config, "a", zero, epochSeconds)
        val room = 1024 - (base + suffix).toByteArray(Charsets.UTF_8).size + 1
        val path = S3CopyPaths.run(config, "a".repeat(room), zero, epochSeconds)
        assertEquals(1024, (path + suffix).toByteArray(Charsets.UTF_8).size)
        assertThrows(IllegalArgumentException::class.java) {
            S3CopyPaths.run(config, "a".repeat(room + 1), zero, epochSeconds)
        }
        // One Japanese character is three UTF-8 bytes and nine percent-encoded key bytes.
        val unicodeName = "日".repeat(room / 9) + "a".repeat(room % 9)
        assertEquals(
            1024,
            (S3CopyPaths.run(config, unicodeName, zero, epochSeconds) + suffix)
                .toByteArray(Charsets.UTF_8)
                .size
        )
        assertThrows(IllegalArgumentException::class.java) {
            S3CopyPaths.run(config, unicodeName + "日", zero, epochSeconds)
        }
        // Prefix bytes count too, even when they are not ASCII.
        assertThrows(IllegalArgumentException::class.java) {
            S3CopyPaths.run(config.copy(prefix = "日".repeat(342)), "a", zero, epochSeconds)
        }
    }
}
