/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.tracing;

import datadog.trace.api.interceptor.MutableSpan;
import datadog.trace.api.interceptor.TraceInterceptor;
import java.util.ArrayList;
import java.util.Collection;

public class StorageObjectGetInterceptor implements TraceInterceptor {

  @Override
  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  public Collection<? extends MutableSpan> onTraceComplete(
                                                           final Collection<? extends MutableSpan> trace) {
    final var filtered = new ArrayList<MutableSpan>();
    trace.forEach(s -> {
      final var tags = s.getTags();
      // if no tags, then keep the span and move on to the next one
      if (tags == null || tags.isEmpty()) {
        filtered.add(s);
        return;
      }

      // There are two different errors spans that we want to ignore, both of which are specific to
      // "storage.googleapis.com". One returns a http status code of 404 and the other has an error
      // message
      // that begins with "404 Not Found"
      final var is404 = tags.getOrDefault("http.status_code", "").equals(404) ||
          ((String) tags.getOrDefault("error.msg", "")).startsWith("404 Not Found");
      if (s.isError() && "storage.googleapis.com".equals(tags.getOrDefault("peer.hostname", ""))
          && is404) {
        // Mark these spans as non-errors as this is expected behavior based on our
        // current google storage usage.
        s.setError(false);
      }

      filtered.add(s);
    });

    return filtered;
  }

  @Override
  public int priority() {
    return 404;
  }

}
