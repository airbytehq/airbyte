/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.notification;

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
  private static final String CUSTOMERIO_API_ENDPOINT = "https://api.customer.io/v1/send/email";

  private final HttpClient httpClient = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_2)
      .build();
  private final String apiToken;

  public EmailNotificationClient(final Notification notification) {
    super(notification);
    this.apiToken = System.getenv("CUSTOMERIO_API_KEY");
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
  public boolean notifyConnectionDisabled(final String email,
                                          final String sourceConnector,
                                          final String destinationConnector,
                                          final String jobDescription,
                                          final String logUrl)
      throws IOException, InterruptedException {
    // send email with template, probably more details about the connection other than ID (what else
    // does it need?)
    //
    final String templatePath = "customerio/auto_disable_notification_template.json";
    // email set twice, first to specify who to send to, and second to re-use as an identifier
    return notifyTemplateMessage(templatePath, email, email, sourceConnector, destinationConnector, jobDescription, logUrl);
  }

  @Override
  public boolean notifySuccess(final String message) throws IOException, InterruptedException {
    throw new NotImplementedException();
  }

  @Override
  public boolean notifyFailure(final String message) throws IOException, InterruptedException {
    throw new NotImplementedException();
  }

  private boolean notifyTemplateMessage(final String templatePath, final String... data) throws IOException, InterruptedException {
    final String body = renderJobData(templatePath, data);

    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers.ofString(body))
        .uri(URI.create(CUSTOMERIO_API_ENDPOINT))
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

  private String renderJobData(final String templateFile, final String... data) throws IOException {
    final String template = MoreResources.readResource(templateFile);
    return String.format(template, data);
  }

}
