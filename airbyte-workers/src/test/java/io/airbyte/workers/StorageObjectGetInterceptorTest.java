/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import datadog.trace.api.interceptor.MutableSpan;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class StorageObjectGetInterceptorTest {

  private static class DummySpan implements MutableSpan {

    @SuppressWarnings("PMD")
    private final Map<String, Object> tags = new HashMap<>();
    private boolean error = false;

    @Override
    public long getStartTime() {
      return 0;
    }

    @Override
    public long getDurationNano() {
      return 0;
    }

    @Override
    public CharSequence getOperationName() {
      return null;
    }

    @Override
    public MutableSpan setOperationName(final CharSequence serviceName) {
      return null;
    }

    @Override
    public String getServiceName() {
      return null;
    }

    @Override
    public MutableSpan setServiceName(final String serviceName) {
      return null;
    }

    @Override
    public CharSequence getResourceName() {
      return null;
    }

    @Override
    public MutableSpan setResourceName(final CharSequence resourceName) {
      return null;
    }

    @Override
    public Integer getSamplingPriority() {
      return null;
    }

    @Override
    public MutableSpan setSamplingPriority(final int newPriority) {
      return null;
    }

    @Override
    public String getSpanType() {
      return null;
    }

    @Override
    public MutableSpan setSpanType(final CharSequence type) {
      return null;
    }

    @Override
    public Map<String, Object> getTags() {
      return tags;
    }

    @Override
    public MutableSpan setTag(final String tag, final String value) {
      tags.put(tag, value);
      return this;
    }

    @Override
    public MutableSpan setTag(final String tag, final boolean value) {
      tags.put(tag, value);
      return this;
    }

    @Override
    public MutableSpan setTag(final String tag, final Number value) {
      tags.put(tag, value);
      return this;
    }

    @Override
    public MutableSpan setMetric(final CharSequence metric, final int value) {
      return null;
    }

    @Override
    public MutableSpan setMetric(final CharSequence metric, final long value) {
      return null;
    }

    @Override
    public MutableSpan setMetric(final CharSequence metric, final double value) {
      return null;
    }

    @Override
    public boolean isError() {
      return error;
    }

    @Override
    public MutableSpan setError(final boolean value) {
      error = value;
      return this;
    }

    @Override
    public MutableSpan getRootSpan() {
      return null;
    }

    @Override
    public MutableSpan getLocalRootSpan() {
      return null;
    }

  }

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
