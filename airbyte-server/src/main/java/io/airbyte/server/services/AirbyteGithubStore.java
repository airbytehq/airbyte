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

package io.airbyte.server.services;

import com.google.common.annotations.VisibleForTesting;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse.BodyHandlers;
import java.time.Duration;

/**
 * Convenience class for retrieving files checked into the Airbyte Github repo.
 */
public class AirbyteGithubStore {

  private static final String GITHUB_BASE_URL = "https://raw.githubusercontent.com";
  private static final String SOURCE_DEFINITION_LIST_LOCATION_PATH =
      "/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/seed/source_definitions.yaml";
  private static final String DESTINATION_DEFINITION_LIST_LOCATION_PATH =
      "/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/seed/destination_definitions.yaml";

  private static final HttpClient httpClient = HttpClient.newHttpClient();

  private final String baseUrl;

  public static AirbyteGithubStore production() {
    return new AirbyteGithubStore(GITHUB_BASE_URL);
  }

  public static AirbyteGithubStore test(String testBaseUrl) {
    return new AirbyteGithubStore(testBaseUrl);
  }

  public AirbyteGithubStore(String baseUrl) {
    this.baseUrl = baseUrl;
  }

  public String getLatestDestinations() throws IOException, InterruptedException {
    return getFile(DESTINATION_DEFINITION_LIST_LOCATION_PATH);
  }

  public String getLatestSources() throws IOException, InterruptedException {
    return getFile(SOURCE_DEFINITION_LIST_LOCATION_PATH);
  }

  @VisibleForTesting
  String getFile(String filePathWithSlashPrefix) throws IOException, InterruptedException {
    final var request = HttpRequest
        .newBuilder(URI.create(baseUrl + filePathWithSlashPrefix))
        .timeout(Duration.ofSeconds(1))
        .header("accept", "*/*") // accept any file type
        .build();
    return httpClient.send(request, BodyHandlers.ofString()).body();
  }

}
