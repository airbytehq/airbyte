/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.notification;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.SlackNotificationConfiguration;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.Charset;
import java.util.UUID;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SlackNotificationClientTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(SlackNotificationClientTest.class);

  public static final String WEBHOOK_URL = "http://localhost:";
  private static final String EXPECTED_FAIL_MESSAGE = "Your connection from source-test to destination-test just failed...\n"
      + "This happened with job description\n"
      + "\n"
      + "You can access its logs here: logUrl\n";
  private static final String EXPECTED_SUCCESS_MESSAGE = "Your connection from source-test to destination-test succeeded\n"
      + "This was for job description\n"
      + "\n"
      + "You can access its logs here: logUrl\n";
  private HttpServer server;

  @BeforeEach
  void setup() throws IOException {
    server = HttpServer.create(new InetSocketAddress(0), 0);
    server.setExecutor(null); // creates a default executor
    server.start();
  }

  @AfterEach
  void tearDown() {
    server.stop(1);
  }

  @Test
  void testBadResponseWrongNotificationMessage() throws IOException, InterruptedException {
    final String message = UUID.randomUUID().toString();
    server.createContext("/test", new ServerHandler("Message mismatched"));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + "/test")));
    assertThrows(IOException.class, () -> client.notifyFailure(message));
  }

  @Test
  void testBadWebhookUrl() {
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + "/bad")));
    assertThrows(IOException.class, () -> client.notifyJobFailure("source-test", "destination-test", "job description", "logUrl"));
  }

  @Test
  void testEmptyWebhookUrl() throws IOException, InterruptedException {
    final SlackNotificationClient client =
        new SlackNotificationClient(
            new Notification().withNotificationType(NotificationType.SLACK).withSlackConfiguration(new SlackNotificationConfiguration()));
    assertFalse(client.notifyJobFailure("source-test", "destination-test", "job description", "logUrl"));
  }

  @Test
  void testNotify() throws IOException, InterruptedException {
    final String message = UUID.randomUUID().toString();
    server.createContext("/test", new ServerHandler(message));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + "/test")));
    assertTrue(client.notifyFailure(message));
    assertFalse(client.notifySuccess(message));
  }

  @Test
  void testNotifyJobFailure() throws IOException, InterruptedException {
    server.createContext("/test", new ServerHandler(EXPECTED_FAIL_MESSAGE));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + "/test")));
    assertTrue(client.notifyJobFailure("source-test", "destination-test", "job description", "logUrl"));
  }

  @Test
  void testNotifyJobSuccess() throws IOException, InterruptedException {
    server.createContext("/test", new ServerHandler(EXPECTED_SUCCESS_MESSAGE));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSendOnSuccess(true)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + "/test")));
    assertTrue(client.notifyJobSuccess("source-test", "destination-test", "job description", "logUrl"));
  }

  static class ServerHandler implements HttpHandler {

    final private String expectedMessage;

    public ServerHandler(String expectedMessage) {
      this.expectedMessage = expectedMessage;
    }

    @Override
    public void handle(HttpExchange t) throws IOException {
      final InputStream is = t.getRequestBody();
      final String body = IOUtils.toString(is, Charset.defaultCharset());
      LOGGER.info("Received: '{}'", body);
      JsonNode message = null;
      try {
        message = Jsons.deserialize(body);
      } catch (RuntimeException e) {
        LOGGER.error("Failed to parse JSON from body {}", body, e);
      }
      final String response;
      if (message != null && message.has("text") && expectedMessage.equals(message.get("text").asText())) {
        response = "Notification acknowledged!";
        t.sendResponseHeaders(200, response.length());
      } else {
        response = "Wrong notification message";
        t.sendResponseHeaders(500, response.length());
      }
      final OutputStream os = t.getResponseBody();
      os.write(response.getBytes());
      os.close();
    }

  }

}
