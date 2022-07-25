/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

/**
 * Custom tuple that represents a key/value pair to be included with a metric.
 */
public record MetricAttribute(String key, String value) {}
