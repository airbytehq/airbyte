/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class SlackNotificationClientTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(SlackNotificationClientTest.class);
  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final String TEST_PATH = "/test";
  private static final String DESTINATION_TEST = "destination-test";
  private static final String JOB_DESCRIPTION = "job description";
  private static final String LOG_URL = "logUrl";
  private static final String SOURCE_TEST = "source-test";
  private static final Long JOB_ID = 1L;

  public static final String WEBHOOK_URL = "http://localhost:";
  private static final String EXPECTED_FAIL_MESSAGE = "Your connection from source-test to destination-test just failed...\n"
      + "This happened with job description\n"
      + "\n"
      + "You can access its logs here: logUrl\n"
      + "\n"
      + "Job ID: 1";
  private static final String EXPECTED_SUCCESS_MESSAGE = "Your connection from source-test to destination-test succeeded\n"
      + "This was for job description\n"
      + "\n"
      + "You can access its logs here: logUrl\n"
      + "\n"
      + "Job ID: 1";
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
    server.createContext(TEST_PATH, new ServerHandler("Message mismatched"));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + TEST_PATH)));
    assertThrows(IOException.class, () -> client.notifyFailure(message));
  }

  @Test
  void testBadWebhookUrl() {
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + "/bad")));
    assertThrows(IOException.class, () -> client.notifyJobFailure(SOURCE_TEST, DESTINATION_TEST, JOB_DESCRIPTION, LOG_URL, JOB_ID));
  }

  @Test
  void testEmptyWebhookUrl() throws IOException, InterruptedException {
    final SlackNotificationClient client =
        new SlackNotificationClient(
            new Notification().withNotificationType(NotificationType.SLACK).withSlackConfiguration(new SlackNotificationConfiguration()));
    assertFalse(client.notifyJobFailure(SOURCE_TEST, DESTINATION_TEST, JOB_DESCRIPTION, LOG_URL, JOB_ID));
  }

  @Test
  void testNotify() throws IOException, InterruptedException {
    final String message = UUID.randomUUID().toString();
    server.createContext(TEST_PATH, new ServerHandler(message));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + TEST_PATH)));
    assertTrue(client.notifyFailure(message));
    assertFalse(client.notifySuccess(message));
  }

  @Test
  void testNotifyJobFailure() throws IOException, InterruptedException {
    server.createContext(TEST_PATH, new ServerHandler(EXPECTED_FAIL_MESSAGE));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + TEST_PATH)));
    assertTrue(client.notifyJobFailure(SOURCE_TEST, DESTINATION_TEST, JOB_DESCRIPTION, LOG_URL, JOB_ID));
  }

  @Test
  void testNotifyJobSuccess() throws IOException, InterruptedException {
    server.createContext(TEST_PATH, new ServerHandler(EXPECTED_SUCCESS_MESSAGE));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSendOnSuccess(true)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + TEST_PATH)));
    assertTrue(client.notifyJobSuccess(SOURCE_TEST, DESTINATION_TEST, JOB_DESCRIPTION, LOG_URL, JOB_ID));
  }

  @Test
  void testNotifyConnectionDisabled() throws IOException, InterruptedException {
    final String expectedNotificationMessage = String.format(
        """
        Your connection from source-test to destination-test was automatically disabled because it failed 100 times consecutively or has been failing for 14 days in a row.

        Please address the failing issues to ensure your syncs continue to run. The most recent attempted job description.

        Workspace ID: %s
        Connection ID: %s
        """,
        WORKSPACE_ID, CONNECTION_ID);

    server.createContext(TEST_PATH, new ServerHandler(expectedNotificationMessage));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSendOnSuccess(true)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + TEST_PATH)));
    assertTrue(client.notifyConnectionDisabled("", SOURCE_TEST, DESTINATION_TEST, "job description.", WORKSPACE_ID, CONNECTION_ID));
  }

  @Test
  void testNotifyConnectionDisabledWarning() throws IOException, InterruptedException {
    final String expectedNotificationWarningMessage = String.format(
        """
        Your connection from source-test to destination-test is scheduled to be automatically disabled because it either failed 50 times consecutively or there were only failed jobs in the past 7 days. Once it has failed 100 times consecutively or has been failing for 14 days in a row, the connection will be automatically disabled.

        Please address the failing issues to ensure your syncs continue to run. The most recent attempted job description.

        Workspace ID: %s
        Connection ID: %s
        """,
        WORKSPACE_ID, CONNECTION_ID);

    server.createContext(TEST_PATH, new ServerHandler(expectedNotificationWarningMessage));
    final SlackNotificationClient client =
        new SlackNotificationClient(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSendOnSuccess(true)
            .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook(WEBHOOK_URL + server.getAddress().getPort() + TEST_PATH)));
    assertTrue(client.notifyConnectionDisableWarning("", SOURCE_TEST, DESTINATION_TEST, "job description.", WORKSPACE_ID, CONNECTION_ID));
  }

  static class ServerHandler implements HttpHandler {

    final private String expectedMessage;

    public ServerHandler(final String expectedMessage) {
      this.expectedMessage = expectedMessage;
    }

    @Override
    public void handle(final HttpExchange t) throws IOException {
      final InputStream is = t.getRequestBody();
      final String body = IOUtils.toString(is, Charset.defaultCharset());
      LOGGER.info("Received: '{}'", body);
      JsonNode message = null;
      try {
        message = Jsons.deserialize(body);
      } catch (final RuntimeException e) {
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
      os.write(response.getBytes(StandardCharsets.UTF_8));
      os.close();
    }

  }

}
