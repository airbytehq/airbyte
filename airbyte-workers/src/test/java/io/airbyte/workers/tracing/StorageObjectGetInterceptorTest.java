/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.tracing;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import org.junit.jupiter.api.Test;

class StorageObjectGetInterceptorTest {

  @Test
  void testOnTraceComplete() {
    final var simple = new DummySpan();

    final var unmodifiedError = new DummySpan();
    unmodifiedError.setError(true);
    unmodifiedError.setTag("unmodified", true);

    final var statusCodeError = new DummySpan();
    statusCodeError.setError(true);
    statusCodeError.setTag("peer.hostname", "storage.googleapis.com");
    statusCodeError.setTag("http.status_code", 404);

    final var errorMsgError = new DummySpan();
    errorMsgError.setError(true);
    errorMsgError.setTag("peer.hostname", "storage.googleapis.com");
    errorMsgError.setTag("error.msg", "404 Not Found and is still missing!");

    final var spans = List.of(
        simple, unmodifiedError, statusCodeError, errorMsgError);

    final var interceptor = new StorageObjectGetInterceptor();
    final var actual = interceptor.onTraceComplete(spans);

    assertEquals(spans, actual);
    assertTrue(unmodifiedError.isError());
    assertFalse(statusCodeError.isError());
    assertFalse(errorMsgError.isError());
  }

}
