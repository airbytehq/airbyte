/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static com.google.common.base.Preconditions.checkArgument;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.ACCEPT_TERMS;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.CATALOG;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.CATALOG_SCHEMA;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.PASSWORD;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.PORT;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.PURGE_STAGING_TABLE;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.SERVER_HOSTNAME;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.STAGING_OBJECT_STORE;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.USERNAME;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyStagingStorageConfig.getStarburstGalaxyStagingStorageConfig;

import com.fasterxml.jackson.databind.JsonNode;

public record StarburstGalaxyDestinationConfig(String galaxyServerHostname,
                                               String galaxyPort,
                                               String galaxyUsername,
                                               String galaxyPassword,
                                               String galaxyCatalog,
                                               String galaxyCatalogSchema,
                                               boolean purgeStagingData,
                                               StarburstGalaxyStagingStorageConfig storageConfig) {

  static final String DEFAULT_STARBURST_GALAXY_PORT = "443";
  static final String DEFAULT_STARBURST_GALAXY_CATALOG_SCHEMA = "public";
  static final boolean DEFAULT_PURGE_STAGING_TABLE = true;

  public static StarburstGalaxyDestinationConfig get(final JsonNode config) {
    checkArgument(
        config.has(ACCEPT_TERMS) && config.get(ACCEPT_TERMS).asBoolean(),
        "You must agree to the Starburst Galaxy Terms & Conditions to use this connector.");
    return new StarburstGalaxyDestinationConfig(
        config.get(SERVER_HOSTNAME).asText(),
        config.has(PORT) ? config.get(PORT).asText() : DEFAULT_STARBURST_GALAXY_PORT,
        config.get(USERNAME).asText(),
        config.get(PASSWORD).asText(),
        config.get(CATALOG).asText(),
        config.has(CATALOG_SCHEMA) ? config.get(CATALOG_SCHEMA).asText() : DEFAULT_STARBURST_GALAXY_CATALOG_SCHEMA,
        config.has(PURGE_STAGING_TABLE) ? config.get(PURGE_STAGING_TABLE).asBoolean() : DEFAULT_PURGE_STAGING_TABLE,
        getStarburstGalaxyStagingStorageConfig(config.get(STAGING_OBJECT_STORE)));
  }

}
