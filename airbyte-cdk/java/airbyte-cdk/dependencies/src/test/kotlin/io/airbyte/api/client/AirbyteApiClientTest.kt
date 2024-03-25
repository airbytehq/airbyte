/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.api.client

import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.mockito.Mock
import org.mockito.Mockito
import java.util.concurrent.Callable

class AirbyteApiClientTest {
    @Mock
    private var mockCallable: Callable<*>? = null

    @Nested
    internal inner class RetryWithJitter {
        @Test
        @Throws(Exception::class)
        fun ifSucceedShouldNotRetry() {
            mockCallable = Mockito.mock(Callable::class.java)
            Mockito.`when`(mockCallable.call()).thenReturn("Success!")

            AirbyteApiClient.retryWithJitter<Any>(mockCallable, "test", TEST_JITTER_INTERVAL_SECS, TEST_FINAL_INTERVAL_SECS, TEST_MAX_RETRIES)

            Mockito.verify(mockCallable, Mockito.times(1)).call()
        }

        @Test
        @Throws(Exception::class)
        fun onlyRetryTillMaxRetries() {
            mockCallable = Mockito.mock(Callable::class.java)
            Mockito.`when`(mockCallable.call()).thenThrow(RuntimeException("Bomb!"))

            AirbyteApiClient.retryWithJitter<Any>(mockCallable, "test", TEST_JITTER_INTERVAL_SECS, TEST_FINAL_INTERVAL_SECS, TEST_MAX_RETRIES)

            Mockito.verify(mockCallable, Mockito.times(TEST_MAX_RETRIES)).call()
        }

        @Test
        @Throws(Exception::class)
        fun onlyRetryOnErrors() {
            mockCallable = Mockito.mock(Callable::class.java)
            // Because we succeed on the second try, we should only call the method twice.
            Mockito.`when`(mockCallable.call())
                    .thenThrow(RuntimeException("Bomb!"))
                    .thenReturn("Success!")

            AirbyteApiClient.retryWithJitter<Any>(mockCallable, "test", TEST_JITTER_INTERVAL_SECS, TEST_FINAL_INTERVAL_SECS, 3)

            Mockito.verify(mockCallable, Mockito.times(2)).call()
        }
    }

    companion object {
        // These set of configurations are so each test case takes ~3 secs.
        private const val TEST_JITTER_INTERVAL_SECS = 1
        private const val TEST_FINAL_INTERVAL_SECS = 1
        private const val TEST_MAX_RETRIES = 2
    }
}
