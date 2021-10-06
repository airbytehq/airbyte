/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.EnvConfigs;
import io.prometheus.client.Counter;
import io.prometheus.client.Gauge;
import io.prometheus.client.Histogram;
import io.prometheus.client.exporter.HTTPServer;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * Use the prometheus library to publish prometheus metrics to a specified port. These metrics can
 * be consumed by any agent understanding the OpenMetrics format.
 *
 * This class mainly exists to help Airbyte instrument/debug application on Airbyte Cloud. Within
 * Airbyte Cloud, the metrics are consumed by a Datadog agent and transformed into Datadog metrics
 * as per https://docs.datadoghq.com/integrations/guide/prometheus-metrics/.
 *
 * Open source users are free to turn this on and consume the same metrics.
 */
public class MetricSingleton {

  private static final Logger LOGGER = LoggerFactory.getLogger(MetricSingleton.class);
  private static boolean PUBLISH = new EnvConfigs().getPublishMetrics();

  private static final Map<String, Gauge> nameToGauge = new HashMap<>();
  private static final Map<String, Counter> nameToCounter = new HashMap<>();
  private static final Map<String, Histogram> nameToHistogram = new HashMap<>();

  private static HTTPServer monitoringDaemon;

  // Gauge. See
  // https://docs.datadoghq.com/metrics/agent_metrics_submission/?tab=gauge#monotonic-count.
  /**
   * Track value at a given timestamp.
   *
   * @param name of gauge
   * @param val to set
   */
  public static void setGauge(String name, double val, String description) {
    validateNameAndCheckDescriptionExists(name, description, () -> ifPublish(() -> {
      if (!nameToGauge.containsKey(name)) {
        Gauge gauge = Gauge.build().name(name).help(description).register();
        nameToGauge.put(name, gauge);
      }
      nameToGauge.get(name).set(val);
    }));
  }

  /**
   * Increment value.
   *
   * @param name of gauge
   * @param val to increment
   */
  public static void incrementGauge(String name, double val, String description) {
    validateNameAndCheckDescriptionExists(name, description, () -> ifPublish(() -> {
      if (nameToGauge.containsKey(name)) {
        LOGGER.warn("Overriding existing metric, type: Gauge, name: {}", name);
      }

      if (!nameToGauge.containsKey(name)) {
        Gauge gauge = Gauge.build().name(name).help(description).register();
        nameToGauge.put(name, gauge);
      }
      nameToGauge.get(name).inc(val);
    }));
  }

  /**
   * Decrement value.
   *
   * @param name of gauge
   * @param val to decrement
   */
  public static void decrementGauge(String name, double val, String description) {
    validateNameAndCheckDescriptionExists(name, description, () -> ifPublish(() -> {
      if (!nameToGauge.containsKey(name)) {
        Gauge gauge = Gauge.build().name(name).help(description).register();
        nameToGauge.put(name, gauge);
      }
      nameToGauge.get(name).dec(val);
    }));
  }

  // Counter - Monotonically Increasing. See
  // https://docs.datadoghq.com/metrics/agent_metrics_submission/?tab=count#monotonic-count.
  /**
   * Increment a monotoically increasing counter.
   *
   * @param name of counter
   * @param amt to increment
   */
  public static void incrementCounter(String name, double amt, String description) {
    validateNameAndCheckDescriptionExists(name, description, () -> ifPublish(() -> {
      if (!nameToCounter.containsKey(name)) {
        Counter counter = Counter.build().name(name).help(description).register();
        nameToCounter.put(name, counter);
      }

      nameToCounter.get(name).inc(amt);
    }));
  }

  // Histogram. See
  // https://docs.datadoghq.com/metrics/agent_metrics_submission/?tab=histogram#monotonic-count.
  /**
   * Time code execution.
   *
   * @param name of histogram
   * @param runnable to time
   * @return duration of code execution.
   */
  public static double timeCode(String name, Runnable runnable, String description) {
    var duration = new AtomicReference<>(0.0);
    validateNameAndCheckDescriptionExists(name, description, () -> ifPublish(() -> {
      if (!nameToHistogram.containsKey(name)) {
        Histogram hist = Histogram.build().name(name).help(description).register();
        nameToHistogram.put(name, hist);
      }
      duration.set(nameToHistogram.get(name).time(runnable));
    }));
    return duration.get();
  }

  /**
   * Submit a single execution time.
   *
   * @param name of the underlying histogram.
   * @param time to be recorded.
   */
  public static void recordTime(String name, double time, String description) {
    validateNameAndCheckDescriptionExists(name, description, () -> ifPublish(() -> {
      LOGGER.info("publishing record time, name: {}, time: {}", name, time);

      if (!nameToHistogram.containsKey(name)) {
        Histogram hist = Histogram.build().name(name).help(description).register();
        nameToHistogram.put(name, hist);
      }
      nameToHistogram.get(name).observe(time);
    }));
  }

  private static void ifPublish(Runnable execute) {
    if (PUBLISH) {
      execute.run();
    }
  }

  private static void validateNameAndCheckDescriptionExists(String name, String description, Runnable execute) {
    if (name.contains("-")) {
      throw new RuntimeException("Name can only contain underscores.");
    }
    if (description.isBlank()) {
      throw new RuntimeException("Counter description cannot be blank.");
    }
    execute.run();
  }

  /**
   * Stand up a separate thread to publish metrics to the specified port.
   *
   * @param monitorPort to publish metrics to
   */
  public static void initializeMonitoringServiceDaemon(String monitorPort, Map<String, String> mdc) {
    ifPublish(() -> {
      try {
        MDC.setContextMap(mdc);
        LOGGER.info("Starting prometheus metric server..");
        // The second constructor argument ('true') makes this server start as a separate daemon thread.
        // http://prometheus.github.io/client_java/io/prometheus/client/exporter/HTTPServer.html#HTTPServer-int-boolean-
        monitoringDaemon = new HTTPServer(Integer.parseInt(monitorPort), true);
      } catch (IOException e) {
        LOGGER.error("Error starting up Prometheus publishing server..", e);
      }
    });
  }

  @VisibleForTesting
  public static void closeMonitoringServiceDaemon() {
    monitoringDaemon.close();
    LOGGER.info("Stopping monitoring daemon..");
  }

  @VisibleForTesting
  public static void setToPublish() {
    PUBLISH = true;
  }

}
