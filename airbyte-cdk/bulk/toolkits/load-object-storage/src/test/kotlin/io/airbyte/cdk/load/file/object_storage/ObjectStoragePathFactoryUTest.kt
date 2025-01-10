/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.file.TimeProvider
import io.mockk.every
import io.mockk.impl.annotations.MockK
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class ObjectStoragePathFactoryUTest {
    @MockK lateinit var stream: DestinationStream
    @MockK lateinit var pathConfigProvider: ObjectStoragePathConfigurationProvider
    @MockK lateinit var timeProvider: TimeProvider

    @BeforeEach
    fun setup() {
        every { stream.descriptor } returns DestinationStream.Descriptor("test", "stream")
        every { timeProvider.syncTimeMillis() } returns 0
        every { timeProvider.currentTimeMillis() } returns 1
    }

    @Test
    fun `test matcher with suffix`() {
        every { pathConfigProvider.objectStoragePathConfiguration } returns
            ObjectStoragePathConfiguration(
                "prefix",
                null,
                "path/",
                "ambiguous_filename",
                false,
            )
        val factory = ObjectStoragePathFactory(pathConfigProvider, null, null, timeProvider)

        val matcher = factory.getPathMatcher(stream, "(-\\d+)?")
        val match1 = matcher.match("prefix/path/ambiguous_filename")
        assertNotNull(match1)
        assertNull(match1?.customSuffix)
        val match2 = matcher.match("prefix/path/ambiguous_filename-1")
        assertNotNull(match2)
        assertEquals(match2?.customSuffix, "-1")
    }
}
