/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.notification;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Notification;
import io.airbyte.config.SlackNotificationConfiguration;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.UUID;
import org.apache.logging.log4j.util.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Notification client that uses Slack API for Incoming Webhook to send messages.
 *
 * This class also reads a resource YAML file that defines the template message to send.
 *
 * It is stored as a YAML so that we can easily change the structure of the JSON data expected by
 * the API that we are posting to (and we can write multi-line strings more easily).
 *
 * For example, slack API expects some text message in the { "text" : "Hello World" } field...
 */
public class SlackNotificationClient extends NotificationClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(SlackNotificationClient.class);

  private final HttpClient httpClient = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_2)
      .build();
  private final SlackNotificationConfiguration config;

  public SlackNotificationClient(final Notification notification) {
    super(notification);
    this.config = notification.getSlackConfiguration();
  }

  @Override
  public boolean notifyJobFailure(final String sourceConnector,
                                  final String destinationConnector,
                                  final String jobDescription,
                                  final String logUrl,
                                  final Long jobId)
      throws IOException, InterruptedException {
    return notifyFailure(renderTemplate(
        "slack/failure_slack_notification_template.txt",
        sourceConnector,
        destinationConnector,
        jobDescription,
        logUrl,
        String.valueOf(jobId)));
  }

  @Override
  public boolean notifyJobSuccess(final String sourceConnector,
                                  final String destinationConnector,
                                  final String jobDescription,
                                  final String logUrl,
                                  final Long jobId)
      throws IOException, InterruptedException {
    return notifySuccess(renderTemplate(
        "slack/success_slack_notification_template.txt",
        sourceConnector,
        destinationConnector,
        jobDescription,
        logUrl,
        String.valueOf(jobId)));
  }

  @Override
  public boolean notifyConnectionDisabled(final String receiverEmail,
                                          final String sourceConnector,
                                          final String destinationConnector,
                                          final String jobDescription,
                                          final UUID workspaceId,
                                          final UUID connectionId)
      throws IOException, InterruptedException {
    final String message = renderTemplate(
        "slack/auto_disable_slack_notification_template.txt",
        sourceConnector,
        destinationConnector,
        jobDescription,
        workspaceId.toString(),
        connectionId.toString());

    final String webhookUrl = config.getWebhook();
    if (!Strings.isEmpty(webhookUrl)) {
      return notify(message);
    }
    return false;
  }

  @Override
  public boolean notifyConnectionDisableWarning(final String receiverEmail,
                                                final String sourceConnector,
                                                final String destinationConnector,
                                                final String jobDescription,
                                                final UUID workspaceId,
                                                final UUID connectionId)
      throws IOException, InterruptedException {
    final String message = renderTemplate(
        "slack/auto_disable_warning_slack_notification_template.txt",
        sourceConnector,
        destinationConnector,
        jobDescription,
        workspaceId.toString(),
        connectionId.toString());

    final String webhookUrl = config.getWebhook();
    if (!Strings.isEmpty(webhookUrl)) {
      return notify(message);
    }
    return false;
  }

  private boolean notify(final String message) throws IOException, InterruptedException {
    final ImmutableMap<String, String> body = new Builder<String, String>()
        .put("text", message)
        .build();
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers.ofString(Jsons.serialize(body)))
        .uri(URI.create(config.getWebhook()))
        .header("Content-Type", "application/json")
        .build();
    final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
    if (isSuccessfulHttpResponse(response.statusCode())) {
      LOGGER.info("Successful notification ({}): {}", response.statusCode(), response.body());
      return true;
    } else {
      final String errorMessage = String.format("Failed to deliver notification (%s): %s", response.statusCode(), response.body());
      throw new IOException(errorMessage);
    }
  }

  @Override
  public boolean notifySuccess(final String message) throws IOException, InterruptedException {
    final String webhookUrl = config.getWebhook();
    if (!Strings.isEmpty(webhookUrl) && sendOnSuccess) {
      return notify(message);
    }
    return false;
  }

  @Override
  public boolean notifyFailure(final String message) throws IOException, InterruptedException {
    final String webhookUrl = config.getWebhook();
    if (!Strings.isEmpty(webhookUrl) && sendOnFailure) {
      return notify(message);
    }
    return false;
  }

  /**
   * Use an integer division to check successful HTTP status codes (i.e., those from 200-299), not
   * just 200. https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
   */
  private static boolean isSuccessfulHttpResponse(final int httpStatusCode) {
    return httpStatusCode / 100 == 2;
  }

}
