/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.api.client

import java.util.concurrent.Callable
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.mockito.Mockito

class AirbyteApiClientTest {
    @Nested
    internal inner class RetryWithJitter {
        @Test
        @Throws(Exception::class)
        fun ifSucceedShouldNotRetry() {
            val mockCallable: Callable<Any> = Mockito.mock()
            Mockito.`when`(mockCallable.call()).thenReturn("Success!")

            AirbyteApiClient.retryWithJitter<Any>(
                mockCallable,
                "test",
                TEST_JITTER_INTERVAL_SECS,
                TEST_FINAL_INTERVAL_SECS,
                TEST_MAX_RETRIES
            )

            Mockito.verify(mockCallable, Mockito.times(1)).call()
        }

        @Test
        @Throws(Exception::class)
        fun onlyRetryTillMaxRetries() {
            val mockCallable: Callable<Any> = Mockito.mock()
            Mockito.`when`(mockCallable.call()).thenThrow(RuntimeException("Bomb!"))

            AirbyteApiClient.retryWithJitter<Any>(
                mockCallable,
                "test",
                TEST_JITTER_INTERVAL_SECS,
                TEST_FINAL_INTERVAL_SECS,
                TEST_MAX_RETRIES
            )

            Mockito.verify(mockCallable, Mockito.times(TEST_MAX_RETRIES)).call()
        }

        @Test
        @Throws(Exception::class)
        fun onlyRetryOnErrors() {
            val mockCallable: Callable<Any> = Mockito.mock()
            // Because we succeed on the second try, we should only call the method twice.
            Mockito.`when`(mockCallable.call())
                .thenThrow(RuntimeException("Bomb!"))
                .thenReturn("Success!")

            AirbyteApiClient.retryWithJitter<Any>(
                mockCallable,
                "test",
                TEST_JITTER_INTERVAL_SECS,
                TEST_FINAL_INTERVAL_SECS,
                3
            )

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
