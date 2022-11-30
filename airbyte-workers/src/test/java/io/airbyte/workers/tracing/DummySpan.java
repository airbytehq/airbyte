/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.tracing;

import datadog.trace.api.interceptor.MutableSpan;
import java.util.HashMap;
import java.util.Map;

class DummySpan implements MutableSpan {

  private final Map<String, Object> tags = new HashMap<>();
  private boolean error = false;
  private String operationName = null;
  private String resourceName = null;

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
    return operationName;
  }

  @Override
  public MutableSpan setOperationName(final CharSequence operationName) {
    this.operationName = operationName != null ? operationName.toString() : null;
    return this;
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
    return resourceName;
  }

  @Override
  public MutableSpan setResourceName(final CharSequence resourceName) {
    this.resourceName = resourceName != null ? resourceName.toString() : null;
    return this;
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
