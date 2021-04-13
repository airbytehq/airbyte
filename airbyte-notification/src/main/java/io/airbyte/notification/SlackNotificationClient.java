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

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.SlackNotificationConfiguration;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
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
public class SlackNotificationClient implements NotificationClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(SlackNotificationClient.class);

  private final HttpClient httpClient = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_2)
      .build();
  private final SlackNotificationConfiguration config;

  public SlackNotificationClient(final SlackNotificationConfiguration config) {
    this.config = config;
  }

  @Override
  public boolean notifyJobFailure(String sourceConnector, String destinationConnector, String jobDescription, String logUrl)
      throws IOException, InterruptedException {
    return notify(renderJobData(
        "failure_slack_notification_template.txt",
        sourceConnector,
        destinationConnector,
        jobDescription,
        logUrl));
  }

  private String renderJobData(String templateFile, String sourceConnector, String destinationConnector, String jobDescription, String logUrl)
      throws IOException {
    final String template = MoreResources.readResource(templateFile);
    return String.format(template, sourceConnector, destinationConnector, jobDescription, logUrl);
  }

  @Override
  public boolean notify(final String message) throws IOException, InterruptedException {
    final String webhookUrl = config.getWebhook();
    if (!Strings.isEmpty(webhookUrl)) {
      final ImmutableMap<String, String> body = new Builder<String, String>()
          .put("text", message)
          .build();
      final HttpRequest request = HttpRequest.newBuilder()
          .POST(HttpRequest.BodyPublishers.ofString(Jsons.serialize(body)))
          .uri(URI.create(webhookUrl))
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
    return false;
  }

  /**
   * Use an integer division to check successful HTTP status codes (i.e., those from 200-299), not
   * just 200. https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
   */
  private static boolean isSuccessfulHttpResponse(int httpStatusCode) {
    return httpStatusCode / 100 == 2;
  }

}
