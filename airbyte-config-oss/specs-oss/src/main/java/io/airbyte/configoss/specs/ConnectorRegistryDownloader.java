/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.configoss.specs;

import io.airbyte.configoss.CatalogDefinitionsConfig;
import java.net.URL;
import java.nio.file.Path;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Download connector registry from airbytehq/airbyte repository.
 */
public class ConnectorRegistryDownloader {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConnectorRegistryDownloader.class);
  private static final String REMOTE_OSS_REGISTRY_URL =
      "https://connectors.airbyte.com/files/registries/v0/oss_registry.json";

  /**
   * This method is to create a path to the resource folder in the project. This is so that it's
   * available at runtime via the getResource method.
   */
  public static Path getResourcePath(final String projectPath, final String relativePath) {
    return Path.of(projectPath, "src/main/resources/", relativePath);
  }

  /**
   * This method is to download the OSS catalog from the remote URL and save it to the local resource
   * folder.
   */
  public static void main(final String[] args) throws Exception {
    final String projectPath = args[0];
    final String relativeWritePath = CatalogDefinitionsConfig.getLocalCatalogWritePath();
    final Path writePath = getResourcePath(projectPath, relativeWritePath);

    LOGGER.info("Downloading OSS connector registry from {} to {}", REMOTE_OSS_REGISTRY_URL, writePath);

    final int timeout = 10000;
    FileUtils.copyURLToFile(new URL(REMOTE_OSS_REGISTRY_URL), writePath.toFile(), timeout, timeout);
  }

}
