/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import static java.util.stream.Collectors.joining;

import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpRequest.BodyPublisher;
import java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

public class SnowflakeOAuthUtils {

  private static final String REFRESH_TOKEN_URL = "https://%s/oauth/token-request";
  private static final HttpClient httpClient = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_2)
      .connectTimeout(Duration.ofSeconds(10))
      .build();

  /**
   * Method to make request for a new access token using refresh token and client credentials.
   *
   * @return access token
   */
  public static String getAccessTokenUsingRefreshToken(final String hostName,
                                                       final String clientId,
                                                       final String clientSecret,
                                                       final String refreshCode)
      throws IOException {
    final var refreshTokenUri = String.format(REFRESH_TOKEN_URL, hostName);
    final Map<String, String> requestBody = new HashMap<>();
    requestBody.put("grant_type", "refresh_token");
    requestBody.put("refresh_token", refreshCode);
    try {
      BodyPublisher bodyPublisher = BodyPublishers.ofString(requestBody.keySet().stream()
          .map(key -> key + "=" + URLEncoder.encode(requestBody.get(key), StandardCharsets.UTF_8))
          .collect(joining("&")));
      final HttpRequest request = HttpRequest.newBuilder()
          .POST(bodyPublisher)
          .uri(URI.create(refreshTokenUri))
          .header("Content-Type", "application/x-www-form-urlencoded")
          .header("Accept", "application/json")
          .header("Authorization", "Basic " + new String(
              Base64.getEncoder().encode((clientId + ":" + clientSecret).getBytes())))
          .build();
      final HttpResponse<String> response = httpClient.send(request,
          HttpResponse.BodyHandlers.ofString());
      return Jsons.deserialize(response.body()).get("access_token").asText();
    } catch (final InterruptedException e) {
      throw new IOException("Failed to refreshToken", e);
    }
  }

}
