/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.client;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.concurrent.Callable;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;

public class AirbyteApiClientTest {

  // These set of configurations are so each test case takes ~3 secs.
  private static final int TEST_JITTER_INTERVAL_SECS = 1;
  private static final int TEST_FINAL_INTERVAL_SECS = 1;
  private static final int TEST_MAX_RETRIES = 2;
  @Mock
  private Callable mockCallable;

  @Nested
  class RetryWithJitter {

    @Test
    @DisplayName("Should not retry on success")
    void ifSucceedShouldNotRetry() throws Exception {
      mockCallable = mock(Callable.class);
      when(mockCallable.call()).thenReturn("Success!");

      AirbyteApiClient.retryWithJitter(mockCallable, "test", TEST_JITTER_INTERVAL_SECS, TEST_FINAL_INTERVAL_SECS, TEST_MAX_RETRIES);

      verify(mockCallable, times(1)).call();
    }

    @Test
    @DisplayName("Should retry up to the configured max retries on continued errors")
    void onlyRetryTillMaxRetries() throws Exception {
      mockCallable = mock(Callable.class);
      when(mockCallable.call()).thenThrow(new RuntimeException("Bomb!"));

      AirbyteApiClient.retryWithJitter(mockCallable, "test", TEST_JITTER_INTERVAL_SECS, TEST_FINAL_INTERVAL_SECS, TEST_MAX_RETRIES);

      verify(mockCallable, times(TEST_MAX_RETRIES)).call();

    }

    @Test
    @DisplayName("Should retry only if there are errors")
    void onlyRetryOnErrors() throws Exception {
      mockCallable = mock(Callable.class);
      // Because we succeed on the second try, we should only call the method twice.
      when(mockCallable.call())
          .thenThrow(new RuntimeException("Bomb!"))
          .thenReturn("Success!");

      AirbyteApiClient.retryWithJitter(mockCallable, "test", TEST_JITTER_INTERVAL_SECS, TEST_FINAL_INTERVAL_SECS, 3);

      verify(mockCallable, times(2)).call();

    }

  }

}
