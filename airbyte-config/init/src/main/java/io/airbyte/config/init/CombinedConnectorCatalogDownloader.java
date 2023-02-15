/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.CatalogDefinitionsConfig;
import io.airbyte.config.CombinedConnectorCatalog;
import java.nio.file.Path;

public class CombinedConnectorCatalogDownloader {

  public static void main(final String[] args) throws Exception {
    final Path writePath = CatalogDefinitionsConfig.getLocalCatalogWritePath();
    final String catalogUrl = CatalogDefinitionsConfig.getRemoteOssCatalogUrl();
    final int timeout = 10000;

    final RemoteDefinitionsProvider remoteDefinitionsProvider = new RemoteDefinitionsProvider(catalogUrl, timeout);
    final CombinedConnectorCatalog combinedCatalog = remoteDefinitionsProvider.getRemoteDefinitionCatalog();
    IOs.writeFile(writePath, Jsons.toPrettyString(Jsons.jsonNode(combinedCatalog)));
  }

}
