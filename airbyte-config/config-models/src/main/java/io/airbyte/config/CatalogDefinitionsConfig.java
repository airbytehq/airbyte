/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import java.nio.file.Path;
import java.util.Optional;

public class CatalogDefinitionsConfig {

  private static final String RESOURCE_DIRECTORY_PATH = "src/main/resources/";
  private static final String SEED_SUBDIRECTORY = "seed/";
  private static final String ICON_SUBDIRECTORY = "icons/";
  private static final String LOCAL_CONNECTOR_CATALOG_FILE_NAME = "oss_catalog.json";
  private static final String DEFAULT_LOCAL_CONNECTOR_CATALOG_PATH =
      SEED_SUBDIRECTORY + LOCAL_CONNECTOR_CATALOG_FILE_NAME;

  private static final String REMOTE_OSS_CATALOG_URL =
      "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/oss_catalog.json";

  public static String getLocalConnectorCatalogPath() {
    Optional<String> customCatalogPath = new EnvConfigs().getLocalCatalogPath();
    if (customCatalogPath.isPresent()) {
      return customCatalogPath.get();
    }

    return DEFAULT_LOCAL_CONNECTOR_CATALOG_PATH;

  }

  public static Path getLocalCatalogWritePath() {
    final Path resourcesRoot = Path.of(RESOURCE_DIRECTORY_PATH);

    // We always want to write to the default path
    // This is to prevent overwriting the catalog file in the event we are using a custom catalog path.
    final Path writePath = resourcesRoot.resolve(DEFAULT_LOCAL_CONNECTOR_CATALOG_PATH);
    return writePath;
  }

  public static String getRemoteOssCatalogUrl() {
    return REMOTE_OSS_CATALOG_URL;
  }

  public static String getIconSubdirectory() {
    return ICON_SUBDIRECTORY;
  }

}
