/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.CombinedConnectorCatalog;
import java.nio.file.Path;

public class CombinedConnectorCatalogDownloader {

  public static void main(final String[] args) throws Exception {
    final Path outputRoot = Path.of(args[0]);
    final String outputFileName = args[1];

    final RemoteDefinitionsProvider remoteDefinitionsProvider =
        new RemoteDefinitionsProvider("https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/oss_catalog.json", 10000);
    final CombinedConnectorCatalog combinedCatalog = remoteDefinitionsProvider.getRemoteDefinitionCatalog();
    IOs.writeFile(outputRoot.resolve(outputFileName), Jsons.toPrettyString(Jsons.jsonNode(combinedCatalog)));
  }

}
