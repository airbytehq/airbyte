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

package io.airbyte.integrations.destination.keen;

import static io.airbyte.integrations.destination.keen.KeenDestination.KEEN_BASE_API_PATH;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.time.Duration;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KeenHttpClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(KeenHttpClient.class);
  private static final String keenBaseApiPath = "https://api.keen.io/3.0";
  private static final int MINUTE_MILLIS = 1000 * 60;
  final HttpClient httpClient = HttpClient.newHttpClient();
  final ObjectMapper objectMapper = new ObjectMapper();

  public void eraseStream(String streamToDelete, String projectId, String apiKey)
      throws IOException, InterruptedException {
    eraseStream(streamToDelete, projectId, apiKey, false);
  }

  public void eraseStream(String streamToDelete, String projectId, String apiKey, boolean retried)
      throws IOException, InterruptedException {

    URI deleteUri = URI.create(String.format(
        KEEN_BASE_API_PATH + "/projects/%s/events/%s",
        projectId, streamToDelete));

    HttpRequest request = HttpRequest.newBuilder()
        .uri(deleteUri)
        .timeout(Duration.ofSeconds(30))
        .header("Authorization", apiKey)
        .header("Content-Type", "application/json")
        .DELETE()
        .build();

    HttpResponse<String> response = httpClient.send(request, BodyHandlers.ofString());

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

  public ArrayNode extract(String streamName, String projectId, String apiKey)
      throws IOException, InterruptedException {
    URI extractionUri = URI.create(String.format(
        keenBaseApiPath + "/projects/%s/queries/extraction" +
            "?api_key=%s&timeframe=this_7_years&event_collection=%s",
        projectId, apiKey, streamName));

    HttpRequest request = HttpRequest.newBuilder()
        .uri(extractionUri)
        .timeout(Duration.ofSeconds(30))
        .header("Content-Type", "application/json")
        .build();

    HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

    if (response.statusCode() != 200) {
      throw new IllegalStateException("Server did not return successful response: " + response.body());
    }

    return (ArrayNode) objectMapper.readTree(response.body()).get("result");
  }

  public List<String> getAllCollectionsForProject(String projectId, String apiKey)
      throws IOException, InterruptedException {
    URI listCollectionsUri = URI.create(String.format(
        KEEN_BASE_API_PATH + "/projects/%s/events",
        projectId));

    HttpRequest request = HttpRequest.newBuilder()
        .uri(listCollectionsUri)
        .timeout(Duration.ofSeconds(30))
        .header("Authorization", apiKey)
        .header("Content-Type", "application/json")
        .build();

    HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

    List<KeenCollection> keenCollections = objectMapper.readValue(objectMapper.createParser(response.body()),
        new TypeReference<>() {});

    return keenCollections.stream().map(KeenCollection::getName).collect(Collectors.toList());
  }

  @JsonIgnoreProperties(ignoreUnknown = true)
  private static class KeenCollection {

    private String name;

    public String getName() {
      return name;
    }

    public void setName(String name) {
      this.name = name;
    }

  }

}
