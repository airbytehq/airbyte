/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.services;

import io.airbyte.config.CatalogDefinitionsConfig;
import io.airbyte.config.init.RemoteDefinitionsProvider;
import java.net.URISyntaxException;
import java.time.Duration;

/**
 * Convenience class for retrieving files checked into the Airbyte Github repo.
 */
@SuppressWarnings("PMD.AvoidCatchingThrowable")
public class AirbyteRemoteOssCatalog extends RemoteDefinitionsProvider {

//  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteRemoteOssCatalog.class);
//  private static final EnvConfigs envConfigs = new EnvConfigs();
//  private static final String GITHUB_BASE_URL = "https://raw.githubusercontent.com";
//  private static final String SOURCE_DEFINITION_LIST_LOCATION_PATH =
//      "/airbytehq/airbyte/" + envConfigs.getGithubStoreBranch() + "/airbyte-config/init/src/main/resources/seed/source_definitions.yaml";
//  private static final String DESTINATION_DEFINITION_LIST_LOCATION_PATH =
//      "/airbytehq/airbyte/" + envConfigs.getGithubStoreBranch() + "/airbyte-config/init/src/main/resources/seed/destination_definitions.yaml";
//  private static final HttpClient httpClient = HttpClient.newHttpClient();

  private static final String REMOTE_OSS_CATALOG_URL = CatalogDefinitionsConfig.getRemoteOssCatalogUrl();

  public static AirbyteRemoteOssCatalog production() throws URISyntaxException {
    return new AirbyteRemoteOssCatalog(REMOTE_OSS_CATALOG_URL, Duration.ofSeconds(30));
  }

  public static AirbyteRemoteOssCatalog test(final String testBaseUrl, final Duration timeout) throws URISyntaxException {
    return new AirbyteRemoteOssCatalog(testBaseUrl, timeout);
  }

  // TODO (ben): Remove the need for subclassing if possible
  public AirbyteRemoteOssCatalog(final String baseUrl, final Duration timeout) throws URISyntaxException {
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
