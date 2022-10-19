/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import datadog.trace.api.interceptor.MutableSpan;
import datadog.trace.api.interceptor.TraceInterceptor;
import java.util.ArrayList;
import java.util.Collection;

@SuppressWarnings("PMD")
public class StorageObjectGetInterceptor implements TraceInterceptor {

  @Override
  public Collection<? extends MutableSpan> onTraceComplete(
                                                           final Collection<? extends MutableSpan> trace) {
    final var filtered = new ArrayList<MutableSpan>();
    trace.forEach(s -> {
      System.out.printf("span name: %s; tags: %s; isError: %s%n", s.getResourceName(), s.getTags(),
          s.isError());
      final var tags = s.getTags();
      // if no tags, then keep the span and move on to the next one
      if (tags == null) {
        filtered.add(s);
        return;
      }

      if (tags.getOrDefault("component", "").equals("google-http-client") &&
          tags.getOrDefault("error.message", "").toString().startsWith("404 Not Found")) {
        s.setError(false);
      }
      System.out.printf("span name: %s; tags: %s; isError: %s%n", s.getResourceName(), s.getTags(),
          s.isError());
      filtered.add(s);
    });

    return filtered;
  }

  @Override
  public int priority() {
    return 404;
  }

}
