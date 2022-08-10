/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.services;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.helpers.YamlListToStandardDefinitions;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse.BodyHandlers;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Convenience class for retrieving files checked into the Airbyte Github repo.
 */
@SuppressWarnings("PMD.AvoidCatchingThrowable")
public class AirbyteGithubStore {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteGithubStore.class);

  private static final String GITHUB_BASE_URL = "https://raw.githubusercontent.com";
  private static final String SOURCE_DEFINITION_LIST_LOCATION_PATH =
      "/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/seed/source_definitions.yaml";
  private static final String DESTINATION_DEFINITION_LIST_LOCATION_PATH =
      "/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/seed/destination_definitions.yaml";

  private static final HttpClient httpClient = HttpClient.newHttpClient();

  private final String baseUrl;
  private final Duration timeout;

  public static AirbyteGithubStore production() {
    return new AirbyteGithubStore(GITHUB_BASE_URL, Duration.ofSeconds(30));
  }

  public static AirbyteGithubStore test(final String testBaseUrl, final Duration timeout) {
    return new AirbyteGithubStore(testBaseUrl, timeout);
  }

  public AirbyteGithubStore(final String baseUrl, final Duration timeout) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
  }

  public List<StandardDestinationDefinition> getLatestDestinations() throws InterruptedException {
    try {
      return YamlListToStandardDefinitions.toStandardDestinationDefinitions(getFile(DESTINATION_DEFINITION_LIST_LOCATION_PATH));
    } catch (final Throwable e) {
      LOGGER.warn(
          "Unable to retrieve latest Destination list from Github. Using the list bundled with Airbyte. This warning is expected if this Airbyte cluster does not have internet access.",
          e);
      return Collections.emptyList();
    }
  }

  public List<StandardSourceDefinition> getLatestSources() throws InterruptedException {
    try {
      return YamlListToStandardDefinitions.toStandardSourceDefinitions(getFile(SOURCE_DEFINITION_LIST_LOCATION_PATH));
    } catch (final Throwable e) {
      LOGGER.warn(
          "Unable to retrieve latest Source list from Github. Using the list bundled with Airbyte. This warning is expected if this Airbyte cluster does not have internet access.",
          e);
      return Collections.emptyList();
    }
  }

  @VisibleForTesting
  String getFile(final String filePathWithSlashPrefix) throws IOException, InterruptedException {
    final var request = HttpRequest
        .newBuilder(URI.create(baseUrl + filePathWithSlashPrefix))
        .timeout(timeout)
        .header("accept", "*/*") // accept any file type
        .build();
    final var resp = httpClient.send(request, BodyHandlers.ofString());
    if (resp.statusCode() >= 400) {
      throw new IOException("getFile request ran into status code error: " + resp.statusCode() + "with message: " + resp.getClass());
    }
    return resp.body();
  }

}
