/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.services;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.CatalogDefinitionsConfig;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.helpers.YamlListToStandardDefinitions;
import io.airbyte.config.init.RemoteDefinitionsProvider;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
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
public class AirbyteGithubStore extends RemoteDefinitionsProvider {

//  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteGithubStore.class);
//  private static final EnvConfigs envConfigs = new EnvConfigs();
//  private static final String GITHUB_BASE_URL = "https://raw.githubusercontent.com";
//  private static final String SOURCE_DEFINITION_LIST_LOCATION_PATH =
//      "/airbytehq/airbyte/" + envConfigs.getGithubStoreBranch() + "/airbyte-config/init/src/main/resources/seed/source_definitions.yaml";
//  private static final String DESTINATION_DEFINITION_LIST_LOCATION_PATH =
//      "/airbytehq/airbyte/" + envConfigs.getGithubStoreBranch() + "/airbyte-config/init/src/main/resources/seed/destination_definitions.yaml";
//  private static final HttpClient httpClient = HttpClient.newHttpClient();

  private static final String REMOTE_OSS_CATALOG_URL = CatalogDefinitionsConfig.getRemoteOssCatalogUrl();

  public static AirbyteGithubStore production() throws URISyntaxException {
    return new AirbyteGithubStore(REMOTE_OSS_CATALOG_URL, Duration.ofSeconds(30));
  }

  public static AirbyteGithubStore test(final String testBaseUrl, final Duration timeout) throws URISyntaxException {
    return new AirbyteGithubStore(testBaseUrl, timeout);
  }

  // TODO (ben): Remove the need for subclassing if possible
  public AirbyteGithubStore(final String baseUrl, final Duration timeout) throws URISyntaxException {
    super(baseUrl, timeout.toMillis());
  }

//  TODO (ben): Change the tests so they dont need this
//  @VisibleForTesting
//  String getFile(final String filePathWithSlashPrefix) throws IOException, InterruptedException {
//    final var request = HttpRequest
//        .newBuilder(URI.create(baseUrl + filePathWithSlashPrefix))
//        .timeout(timeout)
//        .header("accept", "*/*") // accept any file type
//        .build();
//    final var resp = httpClient.send(request, BodyHandlers.ofString());
//    final Boolean isErrorResponse = resp.statusCode() / 100 != 2;
//    if (isErrorResponse) {
//      throw new IOException("getFile request ran into status code error: " + resp.statusCode() + "with message: " + resp.getClass());
//    }
//    return resp.body();
//  }

}
