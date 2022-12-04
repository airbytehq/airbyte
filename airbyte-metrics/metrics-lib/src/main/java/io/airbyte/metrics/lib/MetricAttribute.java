/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

/**
 * Custom tuple that represents a key/value pair to be included with a metric.
 * <p>
 * It is up to each {@link MetricClient} implementation to decide what data from this record is used
 * when generating a metric. See the specific implementations of the {@link MetricClient} interface
 * for actual usage.
 */
public record MetricAttribute(String key, String value) {}
