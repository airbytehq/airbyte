/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics;

import com.timgroup.statsd.NonBlockingStatsDClientBuilder;
import com.timgroup.statsd.StatsDClient;

public class DogstatsdMetricSingleton {

  public static void main(final String[] args) throws InterruptedException {
    final StatsDClient client = new NonBlockingStatsDClientBuilder()
        .prefix("statsd")
        .hostname("localhost")
        .port(8125)
        .build();

    // count
    // gauge
    // histogram
    // distribution
    while (true) {
      System.out.println("publishing metric!");
      client.gauge("davin_test_1", 1);
      Thread.sleep(1000);
    }
  }

}
