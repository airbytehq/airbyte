/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.mockk.coVerify
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import java.lang.IllegalStateException
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class MultiProducerChannelTest {
    @MockK(relaxed = true) lateinit var wrapped: Channel<String>

    private lateinit var channel: MultiProducerChannel<String>

    @BeforeEach
    fun setup() {
        channel = MultiProducerChannel(wrapped)
    }

    @Test
    fun `cannot register a producer if channel already closed`() = runTest {
        channel.registerProducer()
        channel.close()
        assertThrows<IllegalStateException> { channel.registerProducer() }
    }

    @Test
    fun `does not close underlying channel while registered producers exist`() = runTest {
        channel.registerProducer()
        channel.registerProducer()

        channel.close()
        coVerify(exactly = 0) { wrapped.close() }
    }

    @Test
    fun `closes underlying channel when no producers are registered`() = runTest {
        channel.registerProducer()
        channel.registerProducer()
        channel.registerProducer()

        channel.close()
        channel.close()
        channel.close()
        coVerify(exactly = 1) { wrapped.close() }
    }

    @Test
    fun `subsequent calls to to close are idempotent`() = runTest {
        channel.registerProducer()
        channel.registerProducer()

        channel.close()
        channel.close()
        channel.close()
        coVerify(exactly = 1) { wrapped.close() }
    }
}
