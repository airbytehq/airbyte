/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import datadog.trace.api.DDTags;
import datadog.trace.api.interceptor.MutableSpan;
import io.opentracing.Span;
import io.opentracing.log.Fields;
import io.opentracing.tag.Tags;
import io.opentracing.util.GlobalTracer;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.Map;

/**
 * Collection of utility methods to help with performance tracing.
 */
public class ApmTraceUtils {

  /**
   * String format for the name of tags added to spans.
   */
  public static final String TAG_FORMAT = "airbyte.%s.%s";

  /**
   * Standard prefix for tags added to spans.
   */
  public static final String TAG_PREFIX = "metadata";

  /**
   * Adds all the provided tags to the currently active span, if one exists. <br />
   * All tags added via this method will use the default {@link #TAG_PREFIX} namespace.
   *
   * @param tags A map of tags to be added to the currently active span.
   */
  public static void addTagsToTrace(final Map<String, Object> tags) {
    addTagsToTrace(tags, TAG_PREFIX);
  }

  /**
   * Adds all provided tags to the currently active span, if one exists, under the provided tag name
   * namespace.
   *
   * @param tags A map of tags to be added to the currently active span.
   * @param tagPrefix The prefix to be added to each custom tag name.
   */
  public static void addTagsToTrace(final Map<String, Object> tags, final String tagPrefix) {
    addTagsToTrace(GlobalTracer.get().activeSpan(), tags, tagPrefix);
  }

  /**
   * Adds all the provided tags to the provided span, if one exists.
   *
   * @param span The {@link Span} that will be associated with the tags.
   * @param tags A map of tags to be added to the currently active span.
   * @param tagPrefix The prefix to be added to each custom tag name.
   */
  public static void addTagsToTrace(final Span span, final Map<String, Object> tags, final String tagPrefix) {
    if (span != null) {
      tags.entrySet().forEach(entry -> {
        span.setTag(formatTag(entry.getKey(), tagPrefix), entry.getValue().toString());
      });
    }
  }

  /**
   * Adds an exception to the currently active span, if one exists.
   *
   * @param t The {@link Throwable} to be added to the currently active span.
   */
  public static void addExceptionToTrace(final Throwable t) {
    addExceptionToTrace(GlobalTracer.get().activeSpan(), t);
  }

  /**
   * Adds an exception to the provided span, if one exists.
   *
   * @param span The {@link Span} that will be associated with the exception.
   * @param t The {@link Throwable} to be added to the provided span.
   */
  public static void addExceptionToTrace(final Span span, final Throwable t) {
    if (span != null) {
      span.setTag(Tags.ERROR, true);
      span.log(Map.of(Fields.ERROR_OBJECT, t));
    }
  }

  /**
   * Adds all the provided tags to the root span.
   *
   * @param tags A map of tags to be added to the root span.
   */
  public static void addTagsToRootSpan(final Map<String, Object> tags) {
    final Span activeSpan = GlobalTracer.get().activeSpan();
    if (activeSpan instanceof MutableSpan) {
      final MutableSpan localRootSpan = ((MutableSpan) activeSpan).getLocalRootSpan();
      tags.entrySet().forEach(entry -> {
        localRootSpan.setTag(formatTag(entry.getKey(), TAG_PREFIX), entry.getValue().toString());
      });
    }
  }

  /**
   * Adds an exception to the root span, if an active one exists.
   *
   * @param t The {@link Throwable} to be added to the provided span.
   */
  public static void recordErrorOnRootSpan(final Throwable t) {
    final Span activeSpan = GlobalTracer.get().activeSpan();
    if (activeSpan != null) {
      activeSpan.setTag(Tags.ERROR, true);
      activeSpan.log(Map.of(Fields.ERROR_OBJECT, t));
    }
    if (activeSpan instanceof MutableSpan) {
      final MutableSpan localRootSpan = ((MutableSpan) activeSpan).getLocalRootSpan();
      localRootSpan.setError(true);
      localRootSpan.setTag(DDTags.ERROR_MSG, t.getMessage());
      localRootSpan.setTag(DDTags.ERROR_TYPE, t.getClass().getName());
      final StringWriter errorString = new StringWriter();
      t.printStackTrace(new PrintWriter(errorString));
      localRootSpan.setTag(DDTags.ERROR_STACK, errorString.toString());
    }
  }

  /**
   * Formats the tag key using {@link #TAG_FORMAT} provided by this utility, using the default tag
   * prefix {@link #TAG_PREFIX}.
   *
   * @param tagKey The tag key to format.
   * @return The formatted tag key.
   */
  public static String formatTag(final String tagKey) {
    return formatTag(tagKey, TAG_PREFIX);
  }

  /**
   * Formats the tag key using {@link #TAG_FORMAT} provided by this utility with the provided tag
   * prefix.
   *
   * @param tagKey The tag key to format.
   * @param tagPrefix The prefix to be added to each custom tag name.
   * @return The formatted tag key.
   */
  public static String formatTag(final String tagKey, final String tagPrefix) {
    return String.format(TAG_FORMAT, tagPrefix, tagKey);
  }

}
