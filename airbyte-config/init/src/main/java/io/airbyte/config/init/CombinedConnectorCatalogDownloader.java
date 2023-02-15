/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.CombinedConnectorCatalog;
import io.airbyte.config.EnvConfigs;
import java.nio.file.Path;

public class CombinedConnectorCatalogDownloader {
  private static final String RESOURCE_DIRECTORY_PATH = "src/main/resources/";
  private static final String LOCAL_CONNECTOR_CATALOG_PATH = new EnvConfigs().getLocalConnectorCatalogPath();

  public static void main() throws Exception {
    final Path resourcesRoot = Path.of(RESOURCE_DIRECTORY_PATH);
    final Path writePath = resourcesRoot.resolve(LOCAL_CONNECTOR_CATALOG_PATH);

    // TODO (ben) - get url from config
    final String catalogUrl = "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/oss_catalog.json";
    final int timeout = 10000;

    final RemoteDefinitionsProvider remoteDefinitionsProvider = new RemoteDefinitionsProvider(catalogUrl, timeout);

    final CombinedConnectorCatalog combinedCatalog = remoteDefinitionsProvider.getRemoteDefinitionCatalog();
    IOs.writeFile(writePath, Jsons.toPrettyString(Jsons.jsonNode(combinedCatalog)));
  }

}
