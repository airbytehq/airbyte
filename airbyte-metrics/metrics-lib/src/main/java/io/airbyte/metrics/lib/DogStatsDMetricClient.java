/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import com.google.common.annotations.VisibleForTesting;
import com.timgroup.statsd.NonBlockingStatsDClientBuilder;
import com.timgroup.statsd.StatsDClient;
import io.airbyte.config.Configs;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;

/**
 * Light wrapper around the DogsStatsD client to make using the client slightly more ergonomic.
 * <p>
 * This class mainly exists to help Airbyte instrument/debug application on Airbyte Cloud. The
 * methods here do not fail loudly to prevent application disruption.
 * <p>
 * Open source users are free to turn this on and consume the same metrics.
 * <p>
 * This class is intended to be used in conjunction with {@link Configs#getPublishMetrics()}.
 * <p>
 * Any {@link MetricAttribute}s provided with the metric data are sent as tags created by joining
 * the {@code key} and {@code value} property of each {@link MetricAttribute} with a
 * {@link #TAG_DELIMITER} delimiter.
 */
@Slf4j
public class DogStatsDMetricClient implements MetricClient {

  private static final String TAG_DELIMITER = ":";

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
        .constantTags(config.constantTags.toArray(new String[0]))
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
   * @param attributes
   */
  @Override
  public void count(final MetricsRegistry metric, final long amt, final MetricAttribute... attributes) {
    if (instancePublish) {
      if (statsDClient == null) {
        // do not loudly fail to prevent application disruption
        log.warn("singleton not initialized, count {} not emitted", metric);
        return;
      }

      log.info("publishing count, name: {}, value: {}, attributes: {}", metric, amt, attributes);
      statsDClient.count(metric.getMetricName(), amt, toTags(attributes));
    }
  }

  /**
   * Record the latest value for a gauge.
   *
   * @param metric
   * @param val to record.
   * @param attributes
   */
  @Override
  public void gauge(final MetricsRegistry metric, final double val, final MetricAttribute... attributes) {
    if (instancePublish) {
      if (statsDClient == null) {
        // do not loudly fail to prevent application disruption
        log.warn("singleton not initialized, gauge {} not emitted", metric);
        return;
      }

      log.info("publishing gauge, name: {}, value: {}, attributes: {}", metric, val, attributes);
      statsDClient.gauge(metric.getMetricName(), val, toTags(attributes));
    }
  }

  @Override
  public void distribution(final MetricsRegistry metric, final double val, final MetricAttribute... attributes) {
    if (instancePublish) {
      if (statsDClient == null) {
        // do not loudly fail to prevent application disruption
        log.warn("singleton not initialized, distribution {} not emitted", metric);
        return;
      }

      log.info("recording distribution, name: {}, value: {}, attributes: {}", metric, val, attributes);
      statsDClient.distribution(metric.getMetricName(), val, toTags(attributes));
    }
  }

  /**
   * Converts each {@link MetricAttribute} tuple to a list of tags consumable by StatsD.
   *
   * @param attributes An array of {@link MetricAttribute} tuples.
   * @return An array of tag values.
   */
  private String[] toTags(final MetricAttribute... attributes) {
    return Stream.of(attributes).map(a -> String.join(TAG_DELIMITER, a.key(), a.value())).collect(Collectors.toList()).toArray(new String[] {});
  }

}
