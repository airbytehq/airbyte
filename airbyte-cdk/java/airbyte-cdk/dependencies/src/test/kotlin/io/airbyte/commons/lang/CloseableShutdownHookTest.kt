/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.lang

import java.io.InputStream
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class CloseableShutdownHookTest {
    @Test
    @Throws(Exception::class)
    fun testRegisteringShutdownHook() {
        val closeable = Mockito.mock(InputStream::class.java)
        val autoCloseable = Mockito.mock(CloseableQueue::class.java)
        val notCloseable = "Not closeable"

        val thread =
            CloseableShutdownHook.buildShutdownHookThread(
                closeable,
                autoCloseable,
                notCloseable,
            )
        thread.run()

        Mockito.verify(closeable, Mockito.times(1)).close()
        Mockito.verify(autoCloseable, Mockito.times(1)).close()
    }
}
