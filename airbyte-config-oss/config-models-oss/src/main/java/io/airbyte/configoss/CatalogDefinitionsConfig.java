/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.configoss;

import java.util.Optional;

public class CatalogDefinitionsConfig {

  private static final String SEED_SUBDIRECTORY = "seed/";
  private static final String ICON_SUBDIRECTORY = "icons/";
  private static final String LOCAL_CONNECTOR_CATALOG_FILE_NAME = "oss_registry.json";
  private static final String DEFAULT_LOCAL_CONNECTOR_CATALOG_PATH =
      SEED_SUBDIRECTORY + LOCAL_CONNECTOR_CATALOG_FILE_NAME;

  public static String getLocalConnectorCatalogPath() {
    final Optional<String> customCatalogPath = new EnvConfigs().getLocalCatalogPath();
    if (customCatalogPath.isPresent()) {
      return customCatalogPath.get();
    }

    return DEFAULT_LOCAL_CONNECTOR_CATALOG_PATH;

  }

  public static String getIconSubdirectory() {
    return ICON_SUBDIRECTORY;
  }

}
