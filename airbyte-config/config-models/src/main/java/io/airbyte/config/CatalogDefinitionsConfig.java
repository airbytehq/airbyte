/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import java.nio.file.Path;

public class CatalogDefinitionsConfig {

  private static final String RESOURCE_DIRECTORY_PATH = "src/main/resources/";
  private static final String LOCAL_CONNECTOR_CATALOG_FILE_NAME = "oss_catalog.json";
  private static final String SEED_SUBDIRECTORY = "seed/";

  private static final String REMOTE_OSS_CATALOG_URL =
      "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/oss_catalog.json";

  public static String getLocalConnectorCatalogPath() {
    return SEED_SUBDIRECTORY + LOCAL_CONNECTOR_CATALOG_FILE_NAME;
  }

  public static Path getLocalCatalogWritePath() {
    final Path resourcesRoot = Path.of(RESOURCE_DIRECTORY_PATH);
    final Path writePath = resourcesRoot.resolve(getLocalConnectorCatalogPath());
    return writePath;
  }

  public static String getRemoteOssCatalogUrl() {
    return REMOTE_OSS_CATALOG_URL;
  }

}
