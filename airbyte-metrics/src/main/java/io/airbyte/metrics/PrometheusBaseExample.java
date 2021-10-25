/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics;

import io.prometheus.client.Counter;
import io.prometheus.client.Gauge;
import io.prometheus.client.Histogram;
import io.prometheus.client.exporter.HTTPServer;
import java.io.IOException;

public class PrometheusBaseExample {

  // The following represents a class we want to add instrumentation
  // (metrics) to:
  public static class AnInstrumentedClass {

    // Number and type of metrics per class is left on discretion
    // of a Developer.
    // A "namespace()" here sets the prefix of a metric.
    static final Counter counter = Counter.build().namespace("app_prom_java").name("my_counter").help("This is my counter").register();
    static final Gauge gauge = Gauge.build().name("test_metric_gauges").help("test scheduler metric").register();
    static final Histogram histogram = Histogram.build().namespace("app_prom_java").name("my_histogram").help("This is my histogram").register();
    // static final Summary summary =
    // Summary.build().namespace("app_prom_java").name("my_summary").help("This is my
    // summary").register();

    public static void doSomething() {
      // Here goes some business logic. Whenever we want to report
      // something to a monitoring system -- we update a corresponding
      // metrics object, i.e.:

      // counter.inc(rand(0, 5));

      gauge.set(rand(-5, 10));
      // histogram.observe(rand(0, 5));
      // summary.observe(rand(0, 5));
    }

    private static double rand(final double min, final double max) {
      return min + (Math.random() * (max - min));
    }

  }

  public static void main(final String[] args) {
    try {
      // The second constructor argument ('true') makes this server start as a separate daemon thread.
      // http://prometheus.github.io/client_java/io/prometheus/client/exporter/HTTPServer.html#HTTPServer-int-boolean-
      new HTTPServer(Integer.parseInt("8081"), true);
    } catch (final IOException e) {}

    // The following block along with an instance of the instrumented
    // class simulates activity inside instrumented class object, which
    // we may track later by watching metrics' values:
    while (true) {
      try {
        AnInstrumentedClass.doSomething();

        Thread.sleep(1000);
      } catch (final InterruptedException e) {
        e.printStackTrace();
      }
    }

  }

}
