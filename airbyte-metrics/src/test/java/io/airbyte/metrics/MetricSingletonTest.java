/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Map;
import java.util.Random;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

/**
 * Since Prometheus publishes metrics at a specific port, we can test our wrapper by querying the
 * port and validating the response.
 */
public class MetricSingletonTest {

  private static final HttpClient HTTP_CLIENT = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_1_1)
      .connectTimeout(Duration.ofSeconds(10))
      .build();

  private static int availPort;

  @BeforeAll
  public static void setUp() throws IOException {
    // try to grab an available port.
    try (final ServerSocket socket = new ServerSocket(0);) {
      availPort = socket.getLocalPort();
    }

    MetricSingleton.initializeMonitoringServiceDaemon(String.valueOf(availPort), Map.of(), true);
  }

  @AfterAll
  public static void tearDown() {
    MetricSingleton.getInstance().closeMonitoringServiceDaemon();
  }

  @Nested
  class Validation {

    @Test
    public void testNameWithDashFails() {
      assertThrows(RuntimeException.class, () -> MetricSingleton.getInstance().incrementCounter("bad-name", 0.0, "name with dashes are not allowed"));
    }

    @Test
    public void testNoDescriptionFails() {
      assertThrows(RuntimeException.class, () -> MetricSingleton.getInstance().incrementCounter("good_name", 0.0, null));
    }

  }

  @Test
  public void testCounter() throws InterruptedException, IOException {
    final var metricName = "test_counter";
    final var rand = new Random();
    for (int i = 0; i < 5; i++) {
      MetricSingleton.getInstance().incrementCounter(metricName, rand.nextDouble() * 2, "testing counter");
      Thread.sleep(500);
    }

    final HttpResponse<String> response = getPublishedPrometheusMetric();
    assertTrue(response.body().contains(metricName));
  }

  @Test
  public void testGauge() throws InterruptedException, IOException {
    final var metricName = "test_gauge";
    final var rand = new Random();
    for (int i = 0; i < 5; i++) {
      MetricSingleton.getInstance().incrementCounter(metricName, rand.nextDouble() * 2, "testing gauge");
      Thread.sleep(500);
    }

    final HttpResponse<String> response = getPublishedPrometheusMetric();
    assertTrue(response.body().contains(metricName));
  }

  @Test
  public void testTimer() throws InterruptedException, IOException {
    final var metricName = "test_timer";
    final var rand = new Random();
    for (int i = 0; i < 5; i++) {
      MetricSingleton.getInstance().recordTime(metricName, rand.nextDouble() * 2, "testing time");
      Thread.sleep(500);
    }

    final HttpResponse<String> response = getPublishedPrometheusMetric();
    assertTrue(response.body().contains(metricName));
  }

  private HttpResponse<String> getPublishedPrometheusMetric() throws IOException, InterruptedException {
    final HttpRequest request = HttpRequest.newBuilder().GET().uri(URI.create("http://localhost:" + availPort)).build();
    return HTTP_CLIENT.send(request, HttpResponse.BodyHandlers.ofString());
  }

}
