/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics;

import com.timgroup.statsd.NonBlockingStatsDClientBuilder;
import com.timgroup.statsd.StatsDClient;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DogstatsdMetricSingleton {

  public static void main(final String[] args) throws InterruptedException {
    final StatsDClient client = new NonBlockingStatsDClientBuilder()
        .prefix("test_a")
        .hostname(System.getenv("DD_AGENT_HOST"))
        .port(Integer.parseInt(System.getenv("DD_DOGSTATSD_PORT")))
        .build();

    // count
    // gauge
    // histogram
    // distribution
    while (true) {
      System.out.println("publishing metric!");
      client.gauge("davin_test_1", 1);
      client.count("davin_test_1_counter", 1, "test_1:dev");
      Thread.sleep(1000);
    }
  }

}
