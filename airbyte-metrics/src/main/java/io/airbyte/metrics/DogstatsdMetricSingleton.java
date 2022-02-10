/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics;

import com.timgroup.statsd.NonBlockingStatsDClientBuilder;
import com.timgroup.statsd.StatsDClient;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;

@Slf4j
public class DogstatsdMetricSingleton {

  private static StatsDClient instance;
  private static boolean instancePublish = false;

  public static synchronized StatsDClient getInstance() {
    if (instance == null) {
      throw new RuntimeException("You must initialize configuration with the initializeMonitoringServiceDaemon() method before getting an instance.");
    }
    return instance;
  }

  public synchronized static void initializeDogStatsdDaemon(final String appName, final Map<String, String> mdc, final boolean publish) {
    if (instance != null) {
      throw new RuntimeException("You cannot initialize configuration more than once.");
    }
    if (publish) {
      MDC.setContextMap(mdc);
      log.info("Starting DogStatsD client..");
      // The second constructor argument ('true') makes this server start as a separate daemon thread.
      // http://prometheus.github.io/client_java/io/prometheus/client/exporter/HTTPServer.html#HTTPServer-int-boolean-
      instancePublish = true;
      instance = new NonBlockingStatsDClientBuilder()
          .prefix(appName)
          .hostname(System.getenv("DD_AGENT_HOST"))
          .port(Integer.parseInt(System.getenv("DD_DOGSTATSD_PORT")))
          .build();
    }
  }

  public static void count(final String name, final double amt, final String... tags) {
    if (instancePublish) {
      instance.count(name, amt, tags);
    }
  }

  // gauge
  // histogram
  // distribution

  public static void main(final String[] args) throws InterruptedException {
    final StatsDClient client = new NonBlockingStatsDClientBuilder()
        .prefix("test_a")
        .hostname(System.getenv("DD_AGENT_HOST"))
        .port(Integer.parseInt(System.getenv("DD_DOGSTATSD_PORT")))
        .build();

    while (true) {
      System.out.println("publishing metric!");
      client.gauge("davin_test_1", 1);
      client.count("davin_test_1_counter", 1, "test_1:dev");
      Thread.sleep(1000);
    }
  }

}
