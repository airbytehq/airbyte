/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

/**
 * Interface representing an Airbyte Application to collect metrics for. This interface is present
 * as Java doesn't support enum inheritance as of Java 17. We use a shared interface so this
 * interface can be used in the {@link MetricsRegistry} enum.
 */
public interface MetricEmittingApp {

  String getApplicationName();

}
