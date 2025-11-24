/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfigFactory;
import lombok.extern.slf4j.Slf4j;
import org.jetbrains.annotations.NotNull;

@Slf4j
public class IcebergCloudDestination extends BaseIcebergDestination {

  public IcebergCloudDestination() {}

  @Override
  public String getSpecJsonString() throws Exception {
    return MoreResources.readResource("spec-cloud.json");
  }

  @Override
  public IcebergCatalogConfig getCatalogConfig(@NotNull JsonNode config) {
    return IcebergCatalogConfigFactory.fromJsonNodeConfig(config);
  }

}
