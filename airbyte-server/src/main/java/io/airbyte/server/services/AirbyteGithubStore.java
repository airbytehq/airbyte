/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.services;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.helpers.YamlListToStandardDefinitions;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.exceptions.HttpClientResponseException;
import io.micronaut.http.uri.UriBuilder;
import java.io.IOException;
import java.net.URI;
import java.util.Collections;
import java.util.List;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Convenience class for retrieving files checked into the Airbyte Github repo.
 */
@Singleton
public class AirbyteGithubStore {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteGithubStore.class);

  private static final String SOURCE_DEFINITION_LIST_LOCATION_PATH =
      "/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/seed/source_definitions.yaml";
  private static final String DESTINATION_DEFINITION_LIST_LOCATION_PATH =
      "/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/seed/destination_definitions.yaml";

  @Inject
  @Named("githubHttpClient")
  private HttpClient githubHttpClient;

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
  String getFile(final String filePathWithSlashPrefix) throws IOException {
    final URI uri = UriBuilder.of(filePathWithSlashPrefix).build();
    final HttpRequest request = HttpRequest.GET(uri)
        .accept("*/*");
    try {
      return githubHttpClient.toBlocking().retrieve(request, String.class);
    } catch (final HttpClientResponseException e) {
      throw new IOException("getFile request ran into status code error: " + e.getStatus().getCode() + "with message: " + e.getMessage());
    }
  }

}
