/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.airbyte.metrics.lib.ApmTraceUtils.TAG_FORMAT;
import static io.airbyte.metrics.lib.ApmTraceUtils.TAG_PREFIX;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.opentracing.Span;
import io.opentracing.Tracer;
import io.opentracing.util.GlobalTracerTestUtil;
import java.util.Map;
import org.junit.After;
import org.junit.Before;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link ApmTraceUtils} class.
 */
class ApmTraceUtilsTest {

  private static final String TAG_1 = "tag1";
  private static final String TAG_2 = "tag2";
  private static final String VALUE_1 = "foo";
  private static final String VALUE_2 = "bar";
  private static final Map<String, Object> TAGS = Map.of(TAG_1, VALUE_1, TAG_2, VALUE_2);

  @Before
  @After
  public void clearGlobalTracer() {
    GlobalTracerTestUtil.resetGlobalTracer();
  }

  @Test
  void testAddingTags() {
    final Span span = mock(Span.class);
    final Tracer tracer = mock(Tracer.class);
    when(tracer.activeSpan()).thenReturn(span);
    GlobalTracerTestUtil.setGlobalTracerUnconditionally(tracer);
    ApmTraceUtils.addTagsToTrace(TAGS);
    verify(span, times(1)).setTag(String.format(TAG_FORMAT, TAG_PREFIX, TAG_1), VALUE_1);
    verify(span, times(1)).setTag(String.format(TAG_FORMAT, TAG_PREFIX, TAG_2), VALUE_2);
  }

  @Test
  void testAddingTagsWithPrefix() {
    final Span span = mock(Span.class);
    final Tracer tracer = mock(Tracer.class);
    when(tracer.activeSpan()).thenReturn(span);
    GlobalTracerTestUtil.setGlobalTracerUnconditionally(tracer);
    final String tagPrefix = "prefix";
    ApmTraceUtils.addTagsToTrace(TAGS, tagPrefix);
    verify(span, times(1)).setTag(String.format(TAG_FORMAT, tagPrefix, TAG_1), VALUE_1);
    verify(span, times(1)).setTag(String.format(TAG_FORMAT, tagPrefix, TAG_2), VALUE_2);
  }

  @Test
  void testAddingTagsToSpanWithPrefix() {
    final String tagPrefix = "prefix";
    final Span span = mock(Span.class);
    ApmTraceUtils.addTagsToTrace(span, TAGS, tagPrefix);
    verify(span, times(1)).setTag(String.format(TAG_FORMAT, tagPrefix, TAG_1), VALUE_1);
    verify(span, times(1)).setTag(String.format(TAG_FORMAT, tagPrefix, TAG_2), VALUE_2);
  }

  @Test
  void testAddingTagsToNullSpanWithPrefix() {
    final String tagPrefix = "prefix";
    Assertions.assertDoesNotThrow(() -> ApmTraceUtils.addTagsToTrace(null, TAGS, tagPrefix));
  }

}
