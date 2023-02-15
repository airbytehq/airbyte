/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.CombinedConnectorCatalog;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.constants.CatalogDefinitions;
import java.nio.file.Path;

public class CombinedConnectorCatalogDownloader {
  public static void main() throws Exception {
    final Path writePath = CatalogDefinitions.getLocalCatalogWritePath();
    final String catalogUrl = CatalogDefinitions.getRemoteOssCatalogUrl();
    final int timeout = 10000;

    final RemoteDefinitionsProvider remoteDefinitionsProvider = new RemoteDefinitionsProvider(catalogUrl, timeout);
    final CombinedConnectorCatalog combinedCatalog = remoteDefinitionsProvider.getRemoteDefinitionCatalog();
    IOs.writeFile(writePath, Jsons.toPrettyString(Jsons.jsonNode(combinedCatalog)));
  }

}
