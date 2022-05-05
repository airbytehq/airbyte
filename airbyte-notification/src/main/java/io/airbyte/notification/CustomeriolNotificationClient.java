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
import java.util.UUID;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Notification client that uses customer.io API send emails.
 */
public class CustomeriolNotificationClient extends NotificationClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(CustomeriolNotificationClient.class);

  // Once the configs are editable through the UI, these should be stored in
  // airbyte-config/models/src/main/resources/types/CustomerioNotificationConfiguration.yaml
  // - SENDER_EMAIL
  // - receiver email
  // - customer.io identifier email
  // - customer.io TRANSACTION_MESSAGE_ID

  // DEFAULT_TRANSACTION_MESSAGE_ID is currently unused but the template can be used for any generic
  // messaging.
  // private static final String DEFAULT_TRANSACTION_MESSAGE_ID = "6";
  private static final String AUTO_DISABLE_TRANSACTION_MESSAGE_ID = "7";
  private static final String AUTO_DISABLE_WARNING_TRANSACTION_MESSAGE_ID = "8";

  private static final String CUSTOMERIO_EMAIL_API_ENDPOINT = "https://api.customer.io/v1/send/email";
  private static final String AUTO_DISABLE_NOTIFICATION_TEMPLATE_PATH = "customerio/auto_disable_notification_template.json";

  private final HttpClient httpClient;
  private final String apiToken;
  private final String emailApiEndpoint;

  public CustomeriolNotificationClient(final Notification notification) {
    super(notification);
    this.apiToken = System.getenv("CUSTOMERIO_API_KEY");
    this.emailApiEndpoint = CUSTOMERIO_EMAIL_API_ENDPOINT;
    this.httpClient = HttpClient.newBuilder()
        .version(HttpClient.Version.HTTP_2)
        .build();
  }

  @VisibleForTesting
  public CustomeriolNotificationClient(final Notification notification,
                                       final String apiToken,
                                       final String emailApiEndpoint,
                                       final HttpClient httpClient) {
    super(notification);
    this.apiToken = apiToken;
    this.emailApiEndpoint = emailApiEndpoint;
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
                                          final UUID workspaceId,
                                          final UUID connectionId)
      throws IOException, InterruptedException {
    final String requestBody = renderTemplate(AUTO_DISABLE_NOTIFICATION_TEMPLATE_PATH, AUTO_DISABLE_TRANSACTION_MESSAGE_ID, receiverEmail,
        receiverEmail, sourceConnector, destinationConnector, jobDescription, workspaceId.toString(), connectionId.toString());
    return notifyByEmail(requestBody);
  }

  @Override
  public boolean notifyConnectionDisableWarning(final String receiverEmail,
                                                final String sourceConnector,
                                                final String destinationConnector,
                                                final String jobDescription,
                                                final UUID workspaceId,
                                                final UUID connectionId)
      throws IOException, InterruptedException {
    final String requestBody = renderTemplate(AUTO_DISABLE_NOTIFICATION_TEMPLATE_PATH, AUTO_DISABLE_WARNING_TRANSACTION_MESSAGE_ID, receiverEmail,
        receiverEmail, sourceConnector, destinationConnector, jobDescription, workspaceId.toString(), connectionId.toString());
    return notifyByEmail(requestBody);
  }

  @Override
  public boolean notifySuccess(final String message) throws IOException, InterruptedException {
    throw new NotImplementedException();
  }

  @Override
  public boolean notifyFailure(final String message) throws IOException, InterruptedException {
    throw new NotImplementedException();
  }

  private boolean notifyByEmail(final String requestBody) throws IOException, InterruptedException {
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers.ofString(requestBody))
        .uri(URI.create(emailApiEndpoint))
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

  public String renderTemplate(final String templateFile, final String... data) throws IOException {
    final String template = MoreResources.readResource(templateFile);
    return String.format(template, data);
  }

}
