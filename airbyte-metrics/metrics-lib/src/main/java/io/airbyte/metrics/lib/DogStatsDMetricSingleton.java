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
public class DogStatsDMetricSingleton {

  private static boolean instancePublish = false;
  private static StatsDClient statsDClient;

  /**
   * Traditional singleton initialize call. Please invoke this before using any methods in this class.
   * Usually called in the main class of the application attempting to publish metrics.
   */
  public synchronized static void initialize(final MetricEmittingApp app, final DatadogClientConfiguration config) {
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
  public synchronized static void flush() {
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
  public static void count(final MetricsRegistry metric, final double amt, final String... tags) {
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
  public static void gauge(final MetricsRegistry metric, final double val, final String... tags) {
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

  /**
   * Submit a single execution time aggregated locally by the Agent - all metric related statistics
   * are calculated agent-side. Be careful using this if there will be multiple agents emitting this
   * metric as this will cause inaccuracy in non-additive metrics e.g. average, median, percentiles
   * etc.
   *
   * The upside of this is this metric is cheaper to calculate than the Distribution type.
   *
   * See https://docs.datadoghq.com/metrics/types/?tab=histogram#metric-types for more information.
   *
   * @param metric
   * @param val of time to record.
   * @param tags
   */
  public static void recordTimeLocal(final MetricsRegistry metric, final double val, final String... tags) {
    if (instancePublish) {
      if (statsDClient == null) {
        // do not loudly fail to prevent application disruption
        log.warn("singleton not initialized, histogram {} not emitted", metric);
        return;
      }

      log.info("recording histogram, name: {}, value: {}, tags: {}", metric, val, tags);
      statsDClient.histogram(metric.getMetricName(), val, tags);
    }
  }

  /**
   * Submit a single execution time aggregated globally by Datadog - all metric related statistics are
   * calculated in Datadog. Use this for precise stats.
   *
   * @param metric
   * @param val of time to record.
   * @param tags
   */
  public static void recordTimeGlobal(final MetricsRegistry metric, final double val, final String... tags) {
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

  /**
   * Wrapper of {@link #recordTimeGlobal(MetricsRegistry, double, String...)} with a runnable for
   * convenience.
   *
   * @param metric
   * @param runnable to time
   * @param tags
   */
  public static void recordTimeGlobal(final MetricsRegistry metric, final Runnable runnable, final String... tags) {
    final long start = System.currentTimeMillis();
    runnable.run();
    final long end = System.currentTimeMillis();
    final long val = end - start;
    recordTimeGlobal(metric, val, tags);
  }

  /**
   * Wrapper around {@link #recordTimeGlobal(MetricsRegistry, double, String...)} with a different
   * name to better represent what this function does.
   *
   * @param metric
   * @param val
   * @param tags
   */
  public static void percentile(final MetricsRegistry metric, final double val, final String... tags) {
    recordTimeGlobal(metric, val, tags);
  }

}
