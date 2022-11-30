/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.keen;

import static io.airbyte.integrations.destination.keen.KeenDestination.KEEN_BASE_API_PATH;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KeenHttpClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(KeenHttpClient.class);
  private static final String keenBaseApiPath = "https://api.keen.io/3.0";
  private static final int MINUTE_MILLIS = 1000 * 60;
  final HttpClient httpClient = HttpClient.newHttpClient();
  final ObjectMapper objectMapper = new ObjectMapper();

  public void eraseStream(final String streamToDelete, final String projectId, final String apiKey)
      throws IOException, InterruptedException {
    eraseStream(streamToDelete, projectId, apiKey, false);
  }

  public void eraseStream(final String streamToDelete, final String projectId, final String apiKey, final boolean retried)
      throws IOException, InterruptedException {

    final URI deleteUri = URI.create(String.format(
        KEEN_BASE_API_PATH + "/projects/%s/events/%s",
        projectId, streamToDelete));

    final HttpRequest request = HttpRequest.newBuilder()
        .uri(deleteUri)
        .timeout(Duration.ofSeconds(30))
        .header("Authorization", apiKey)
        .header("Content-Type", "application/json")
        .DELETE()
        .build();

    final HttpResponse<String> response = httpClient.send(request, BodyHandlers.ofString());

    if (response.statusCode() != 204) {
      if (response.statusCode() == 429 && !retried) {
        LOGGER.info("Deletes limit exceeded. Sleeping 60 seconds.");
        Thread.sleep(MINUTE_MILLIS);
        eraseStream(streamToDelete, projectId, apiKey, true);
      } else {
        throw new IllegalStateException(String.format("Could not erase data from stream designed for overriding: "
            + "%s. Error message: %s", streamToDelete, response.body()));
      }
    }
  }

  public ArrayNode extract(final String streamName, final String projectId, final String apiKey)
      throws IOException, InterruptedException {
    final URI extractionUri = URI.create(String.format(
        keenBaseApiPath + "/projects/%s/queries/extraction" +
            "?api_key=%s&timeframe=this_7_years&event_collection=%s",
        projectId, apiKey, streamName));

    final HttpRequest request = HttpRequest.newBuilder()
        .uri(extractionUri)
        .timeout(Duration.ofSeconds(30))
        .header("Content-Type", "application/json")
        .build();

    final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

    if (response.statusCode() != 200) {
      throw new IllegalStateException("Server did not return successful response: " + response.body());
    }

    return (ArrayNode) objectMapper.readTree(response.body()).get("result");
  }

}
