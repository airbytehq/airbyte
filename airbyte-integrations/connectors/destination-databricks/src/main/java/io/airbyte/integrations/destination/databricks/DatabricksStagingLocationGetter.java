/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Request personal staging locations from Databricks metastore. The equivalent curl command is:
 *
 * <pre>
 * curl --location --request POST \
 *   'https://<server-host>/api/2.1/unity-catalog/temporary-stage-credentials' \
 *   --header 'Authorization: Bearer <personal-access-token>' \
 *   --form 'staging_url="stage://tmp/<username>/file.csv"' \
 *   --form 'operation="PUT"' \
 *   --form 'credential_type="PRESIGNED_URL"'
 * </pre>
 */
public class DatabricksStagingLocationGetter {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksStagingLocationGetter.class);
  private static final String PERSONAL_STAGING_REQUEST_URL = "https://%s/api/2.1/unity-catalog/temporary-stage-credentials";
  private static final String STAGING_URL = "stage://tmp/%s/%s";

  private static final HttpClient httpClient = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_2)
      .connectTimeout(Duration.ofSeconds(10))
      .build();

  private static final Map<String, String> staticRequestParams = Map.of(
      "operation", "PUT",
      "credential_type", "PRESIGNED_URL");

  private static final String PARAM_STAGING_URL = "staging_url";
  private static final String RESPONSE_PRESIGNED_URL = "presigned_url";
  private static final String RESPONSE_URL = "url";
  private static final String RESPONSE_EXPIRATION = "expiration_time";

  private final String username;
  private final String serverHost;
  private final String personalAccessToken;

  public DatabricksStagingLocationGetter(final String username, final String serverHost, final String personalAccessToken) {
    this.username = username;
    this.serverHost = serverHost;
    this.personalAccessToken = personalAccessToken;
  }

  /**
   * @param filePath include path and filename: <path>/<filename>.
   * @return the pre-signed URL for the file in the personal staging location on the metastore.
   */
  public PreSignedUrl getPreSignedUrl(final String filePath) throws IOException, InterruptedException {
    final String stagingUrl = String.format(STAGING_URL, username, filePath);
    LOGGER.info("Requesting Databricks personal staging location for {}", stagingUrl);

    final Map<String, String> requestBody = new HashMap<>(staticRequestParams);
    requestBody.put(PARAM_STAGING_URL, stagingUrl);

    final HttpRequest request = HttpRequest.newBuilder()
        .POST(BodyPublishers.ofString(Jsons.serialize(requestBody)))
        .uri(URI.create(String.format(PERSONAL_STAGING_REQUEST_URL, serverHost)))
        .header("Authorization", "Bearer " + personalAccessToken)
        .build();
    final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

    final JsonNode jsonResponse = Jsons.deserialize(response.body());
    if (jsonResponse.has(RESPONSE_PRESIGNED_URL) && jsonResponse.get(RESPONSE_PRESIGNED_URL).has(RESPONSE_URL) && jsonResponse.get(
        RESPONSE_PRESIGNED_URL).has(RESPONSE_EXPIRATION)) {
      return new PreSignedUrl(
          jsonResponse.get(RESPONSE_PRESIGNED_URL).get(RESPONSE_URL).asText(),
          jsonResponse.get(RESPONSE_PRESIGNED_URL).get(RESPONSE_EXPIRATION).asLong());
    } else {
      final String message = String.format("Failed to get pre-signed URL for %s: %s", stagingUrl, jsonResponse);
      LOGGER.error(message);
      throw new RuntimeException(message);
    }

  }

}
