/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import com.google.common.annotations.VisibleForTesting;
import com.timgroup.statsd.NonBlockingStatsDClientBuilder;
import com.timgroup.statsd.StatsDClient;
import io.airbyte.config.Configs;
import lombok.extern.slf4j.Slf4j;

/**
 * Light wrapper around the DogsStatsD client to make using the client slightly more ergonomic.
 * <p>
 * This class mainly exists to help Airbyte instrument/debug application on Airbyte Cloud. The
 * methods here do not fail loudly to prevent application disruption.
 * <p>
 * Open source users are free to turn this on and consume the same metrics.
 * <p>
 * This class is intended to be used in conjection with {@link Configs#getPublishMetrics()}.
 */
@Slf4j
public class DogStatsDMetricClient implements MetricClient {

  private boolean instancePublish = false;
  private StatsDClient statsDClient;

  /**
   * Traditional singleton initialize call. Please invoke this before using any methods in this class.
   * Usually called in the main class of the application attempting to publish metrics.
   */

  public void initialize(final MetricEmittingApp app, final DatadogClientConfiguration config) {
    if (statsDClient != null) {
      throw new RuntimeException("You cannot initialize configuration more than once.");
    }

    if (!config.publish) {
      // do nothing if we do not want to publish. All metrics methods also do nothing.
      return;
    }

    log.info("Starting DogStatsD client..");
    instancePublish = config.publish;
    statsDClient = new NonBlockingStatsDClientBuilder()
        .prefix(app.getApplicationName())
        .hostname(config.ddAgentHost)
        .port(Integer.parseInt(config.ddPort))
        .build();
  }

  @VisibleForTesting
  @Override
  public synchronized void shutdown() {
    statsDClient = null;
    instancePublish = false;
  }

  /**
   * Increment or decrement a counter.
   *
   * @param metric
   * @param amt to adjust.
   * @param tags
   */
  @Override
  public void count(final MetricsRegistry metric, final long amt, final String... tags) {
    if (instancePublish) {
      if (statsDClient == null) {
        // do not loudly fail to prevent application disruption
        log.warn("singleton not initialized, count {} not emitted", metric);
        return;
      }

      log.info("publishing count, name: {}, value: {}, tags: {}", metric, amt, tags);
      statsDClient.count(metric.getMetricName(), amt, tags);
    }
  }

  /**
   * Record the latest value for a gauge.
   *
   * @param metric
   * @param val to record.
   * @param tags
   */
  @Override
  public void gauge(final MetricsRegistry metric, final double val, final String... tags) {
    if (instancePublish) {
      if (statsDClient == null) {
        // do not loudly fail to prevent application disruption
        log.warn("singleton not initialized, gauge {} not emitted", metric);
        return;
      }

      log.info("publishing gauge, name: {}, value: {}, tags: {}", metric, val, tags);
      statsDClient.gauge(metric.getMetricName(), val, tags);
    }
  }

  @Override
  public void distribution(MetricsRegistry metric, double val, final String... tags) {
    if (instancePublish) {
      if (statsDClient == null) {
        // do not loudly fail to prevent application disruption
        log.warn("singleton not initialized, distribution {} not emitted", metric);
        return;
      }

      log.info("recording distribution, name: {}, value: {}, tags: {}", metric, val, tags);
      statsDClient.distribution(metric.getMetricName(), val, tags);
    }
  }

}
