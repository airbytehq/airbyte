/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import com.timgroup.statsd.NonBlockingStatsDClientBuilder;
import com.timgroup.statsd.StatsDClient;
import lombok.extern.slf4j.Slf4j;

/**
 * Light wrapper around the DogsStatsD client to make using the client slightly more ergonomic.
 * <p>
 * This class mainly exists to help Airbyte instrument/debug application on Airbyte Cloud.
 * <p>
 * Open source users are free to turn this on and consume the same metrics.
 */
@Slf4j
public class DogstatsdMetricSingleton {

  private static DogstatsdMetricSingleton instance;
  private final StatsDClient statsDClient;
  private final boolean instancePublish;

  public static synchronized DogstatsdMetricSingleton getInstance() {
    if (instance == null) {
      throw new RuntimeException("You must initialize configuration with the initialize() method before getting an instance.");
    }
    return instance;
  }

  public synchronized static void initialize(final AirbyteApplication app, final boolean publish) {
    if (instance != null) {
      throw new RuntimeException("You cannot initialize configuration more than once.");
    }
    if (publish) {
      log.info("Starting DogStatsD client..");
      // The second constructor argument ('true') makes this server start as a separate daemon thread.
      // http://prometheus.github.io/client_java/io/prometheus/client/exporter/HTTPServer.html#HTTPServer-int-boolean-
      instance = new DogstatsdMetricSingleton(app.getApplicationName(), publish);
    }
  }

  private DogstatsdMetricSingleton(final String appName, final boolean publish) {
    instancePublish = publish;
    statsDClient = new NonBlockingStatsDClientBuilder()
        .prefix(appName)
        .hostname(System.getenv("DD_AGENT_HOST"))
        .port(Integer.parseInt(System.getenv("DD_DOGSTATSD_PORT")))
        .build();
  }

  /**
   * Increment or decrement a counter.
   *
   * @param metric
   * @param amt to adjust.
   * @param tags
   */
  public void count(final AirbyteMetric metric, final double amt, final String... tags) {
    if (instancePublish) {
      log.info("publishing count, name: {}, value: {}", metric.metricName, amt);
      statsDClient.count(metric.metricName, amt, tags);
    }
  }

  /**
   * Record the latest value for a gauge.
   *
   * @param name of gauge.
   * @param val to record.
   * @param tags
   */
  public void gauge(final AirbyteMetric metric, final double val, final String... tags) {
    if (instancePublish) {
      log.info("publishing gauge, name: {}, value: {}", metric, val);
      statsDClient.gauge(metric.metricName, val, tags);
    }
  }

  /**
   * Submit a single execution time aggregated locally by the Agent. Use this if approximate stats are
   * sufficient.
   *
   * @param name of histogram.
   * @param val of time to record.
   * @param tags
   */
  public void recordTimeLocal(final AirbyteMetric metric, final double val, final String... tags) {
    if (instancePublish) {
      log.info("recording histogram, name: {}, value: {}", metric.metricName, val);
      statsDClient.histogram(metric.metricName, val, tags);
    }
  }

  /**
   * Submit a single execution time aggregated globally by Datadog. Use this for precise stats.
   *
   * @param metric
   * @param val of time to record.
   * @param tags
   */
  public void recordTimeGlobal(final AirbyteMetric metric, final double val, final String... tags) {
    if (instancePublish) {
      log.info("recording distribution, name: {}, value: {}", metric.metricName, val);
      statsDClient.distribution(metric.metricName, val, tags);
    }
  }

  /**
   * Wrapper of {@link #recordTimeGlobal(AirbyteMetric, double, String...)} with a runnable for
   * convenience.
   *
   * @param metric
   * @param runnable to time
   * @param tags
   */
  public void recordTimeGlobal(final AirbyteMetric metric, final Runnable runnable, final String... tags) {
    final long start = System.currentTimeMillis();
    runnable.run();
    final long end = System.currentTimeMillis();
    final long val = end - start;
    recordTimeGlobal(metric, val, tags);
  }

}
