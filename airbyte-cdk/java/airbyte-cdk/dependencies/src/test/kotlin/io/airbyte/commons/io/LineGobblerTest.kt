/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.io

import com.google.common.collect.ImmutableMap
import com.google.common.util.concurrent.MoreExecutors
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import java.io.ByteArrayInputStream
import java.io.InputStream
import java.nio.charset.StandardCharsets
import java.util.concurrent.ExecutorService
import java.util.function.Consumer

internal class LineGobblerTest {
    @Test
    fun readAllLines() {
        val consumer: Consumer<String> = Mockito.mock(Consumer::class.java)
        val `is`: InputStream = ByteArrayInputStream("test\ntest2\n".toByteArray(StandardCharsets.UTF_8))
        val executor: ExecutorService = Mockito.spy(MoreExecutors.newDirectExecutorService())

        executor.submit(LineGobbler(`is`, consumer, executor, ImmutableMap.of()))

        Mockito.verify(consumer).accept("test")
        Mockito.verify(consumer).accept("test2")
        Mockito.verify(executor).shutdown()
    }

    @Test
    fun shutdownOnSuccess() {
        val consumer: Consumer<String> = Mockito.mock(Consumer::class.java)
        val `is`: InputStream = ByteArrayInputStream("test\ntest2\n".toByteArray(StandardCharsets.UTF_8))
        val executor: ExecutorService = Mockito.spy(MoreExecutors.newDirectExecutorService())

        executor.submit(LineGobbler(`is`, consumer, executor, ImmutableMap.of()))

        Mockito.verify(consumer, Mockito.times(2)).accept(ArgumentMatchers.anyString())
        Mockito.verify(executor).shutdown()
    }

    @Test
    fun shutdownOnError() {
        val consumer: Consumer<String> = Mockito.mock(Consumer::class.java)
        Mockito.doThrow(RuntimeException::class.java).`when`(consumer).accept(ArgumentMatchers.anyString())
        val `is`: InputStream = ByteArrayInputStream("test\ntest2\n".toByteArray(StandardCharsets.UTF_8))
        val executor: ExecutorService = Mockito.spy(MoreExecutors.newDirectExecutorService())

        executor.submit(LineGobbler(`is`, consumer, executor, ImmutableMap.of()))

        Mockito.verify(consumer).accept(ArgumentMatchers.anyString())
        Mockito.verify(executor).shutdown()
    }
}
