package io.airbyte.integrations.destination.snowflake.copy

import java.util.UUID
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Test

class S3CopyPathsTest {
    @Test
    fun `run paths include workspace connection and escaped original stream`() {
        val zero = UUID(0, 0)
        val config = S3CopyConfiguration("role", "bucket", "region", zero, zero, zero, "fusion", null)
        val path = S3CopyPaths.run(config, "Orders/日本 %", zero)
        assertEquals(
            "fusion/workspaces/$zero/sources/$zero/connections/$zero/streams/Orders%2F%E6%97%A5%E6%9C%AC%20%25/runs/$zero",
            path,
        )
        assertNotEquals(path, S3CopyPaths.run(config, "Orders/日本 %", UUID(0, 1)))
        assertNotEquals(path, S3CopyPaths.run(config.copy(sourceId = UUID(0, 1)), "Orders/日本 %", zero))
        assertNotEquals(path, S3CopyPaths.run(config.copy(workspaceId = UUID(0, 1)), "Orders/日本 %", zero))
    }

    @Test
    fun `encoding cannot confuse literal percent escapes or relative segments`() {
        assertEquals("a%2Fb", S3CopyPaths.escape("a/b"))
        assertEquals("a%252Fb", S3CopyPaths.escape("a%2Fb"))
        assertEquals("%2E%2E", S3CopyPaths.escape(".."))
        assertEquals("Orders.v1-_~", S3CopyPaths.escape("Orders.v1-_~"))
    }
}
