/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.notification;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.Notification;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Notification client that uses customer.io API send emails.
 */
public class EmailNotificationClient extends NotificationClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(EmailNotificationClient.class);

  // Once the configs are editable through the UI, these should be stored in
  // airbyte-config/models/src/main/resources/types/EmailNotificationConfiguration.yaml
  // - SENDER_EMAIL
  // - receiver email
  // - customer.io identifier email
  // - customer.io TRANSACTION_MESSAGE_ID
  private static final String SENDER_EMAIL = "Airbyte Notification <no-reply@airbyte.io>";
  private static final String TRANSACTION_MESSAGE_ID = "6";

  private static final String CUSTOMERIO_API_ENDPOINT = "https://api.customer.io/v1/send/email";
  private static final String AUTO_DISABLE_NOTIFICATION_TEMPLATE_PATH = "customerio/auto_disable_notification_template.json";

  private final HttpClient httpClient;
  private final String apiToken;
  private final String apiEndpoint;

  public EmailNotificationClient(final Notification notification) {
    super(notification);
    this.apiToken = System.getenv("CUSTOMERIO_API_KEY");
    this.apiEndpoint = CUSTOMERIO_API_ENDPOINT;
    this.httpClient = HttpClient.newBuilder()
        .version(HttpClient.Version.HTTP_2)
        .build();
  }

  @VisibleForTesting
  public EmailNotificationClient(final Notification notification, final String apiToken, final String apiEndpoint, final HttpClient httpClient) {
    super(notification);
    this.apiToken = apiToken;
    this.apiEndpoint = apiEndpoint;
    this.httpClient = httpClient;
  }

  @Override
  public boolean notifyJobFailure(final String sourceConnector, final String destinationConnector, final String jobDescription, final String logUrl)
      throws IOException, InterruptedException {
    throw new NotImplementedException();
  }

  @Override
  public boolean notifyJobSuccess(final String sourceConnector, final String destinationConnector, final String jobDescription, final String logUrl)
      throws IOException, InterruptedException {
    throw new NotImplementedException();
  }

  @Override
  public boolean notifyConnectionDisabled(final String receiverEmail,
                                          final String sourceConnector,
                                          final String destinationConnector,
                                          final String jobDescription,
                                          final String logUrl)
      throws IOException, InterruptedException {
    final String requestBody = renderTemplate(AUTO_DISABLE_NOTIFICATION_TEMPLATE_PATH, TRANSACTION_MESSAGE_ID, SENDER_EMAIL, receiverEmail,
        receiverEmail, sourceConnector, destinationConnector, jobDescription, logUrl);
    return notifyMessage(requestBody);
  }

  @Override
  public boolean notifySuccess(final String message) throws IOException, InterruptedException {
    throw new NotImplementedException();
  }

  @Override
  public boolean notifyFailure(final String message) throws IOException, InterruptedException {
    throw new NotImplementedException();
  }

  private boolean notifyMessage(final String requestBody) throws IOException, InterruptedException {
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers.ofString(requestBody))
        .uri(URI.create(apiEndpoint))
        .header("Content-Type", "application/json")
        .header("Authorization", "Bearer " + apiToken)
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

  /**
   * Use an integer division to check successful HTTP status codes (i.e., those from 200-299), not
   * just 200. https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
   */
  private static boolean isSuccessfulHttpResponse(final int httpStatusCode) {
    return httpStatusCode / 100 == 2;
  }

  @VisibleForTesting
  public String renderTemplate(final String templateFile, final String... data) throws IOException {
    final String template = MoreResources.readResource(templateFile);
    return String.format(template, data);
  }

}
