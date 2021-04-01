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

package io.airbyte.scheduler.persistence.job_tracker;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;
import java.util.Map.Entry;
import org.apache.logging.log4j.util.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SlackNotificationClient implements NotificationClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(SlackNotificationClient.class);

  private final HttpClient httpClient = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_2)
      .build();
  private final ConfigRepository configRepository;

  public SlackNotificationClient(ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  @Override
  public void notifyFailure(String action, Map<String, Object> metadata)
      throws ConfigNotFoundException, IOException, JsonValidationException, InterruptedException {
    metadata = MoreMaps.merge(metadata, generateMetadata(metadata));
    final StandardWorkspace workspace = configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID, true);
    final String webhook = workspace.getFailureNotificationsWebhook();
    if (!Strings.isEmpty(webhook)) {
      final String data = generateData(metadata);
      final HttpRequest request = HttpRequest.newBuilder()
          .POST(HttpRequest.BodyPublishers.ofString(data))
          .uri(URI.create(webhook))
          .header("Content-Type", "application/json")
          .build();
      final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
      LOGGER.info("Failure notification ({}): {}", response.statusCode(), response.body());
    }
  }

  private static String generateData(Map<String, Object> metadata) throws IOException {
    final JsonNode template = Yamls.deserialize(MoreResources.readResource("SlackNotificationTemplate.yml"));
    String data = Jsons.toPrettyString(template);
    for (Entry<String, Object> entry : metadata.entrySet()) {
      final String key = "<" + entry.getKey() + ">";
      if (data.contains(key)) {
        data = data.replaceAll(key, entry.getValue().toString());
      }
    }
    return data;
  }

  private static Map<String, Object> generateMetadata(Map<String, Object> jobData) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    // TODO: Get the correct url to this airbyte instance
    metadata.put("log_url", "http://localhost:8000/source/connection/" + jobData.get("connection_id"));
    return metadata.build();
  }

}
