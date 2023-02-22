/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import io.airbyte.config.CatalogDefinitionsConfig;
import java.net.URL;
import java.nio.file.Path;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CombinedConnectorCatalogDownloader {

  private static final Logger LOGGER = LoggerFactory.getLogger(CombinedConnectorCatalogDownloader.class);

  public static Path getResourcePath(final String projectPath, final String relativePath) {
    return Path.of(projectPath, "src/main/resources/", relativePath);
  }

  public static void main(final String[] args) throws Exception {
    final String projectPath = args[0];
    final String relativeWritePath = CatalogDefinitionsConfig.getLocalCatalogWritePath();
    final Path writePath = getResourcePath(projectPath, relativeWritePath);
    final String catalogUrl = CatalogDefinitionsConfig.getRemoteOssCatalogUrl();
    LOGGER.info("Downloading OSS catalog from {} to {}", catalogUrl, writePath);

    final int timeout = 10000;
    FileUtils.copyURLToFile(new URL(catalogUrl), writePath.toFile(), timeout, timeout);
  }

}
