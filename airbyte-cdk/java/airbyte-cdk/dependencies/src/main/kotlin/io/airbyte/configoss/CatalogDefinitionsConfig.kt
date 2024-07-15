/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss

object CatalogDefinitionsConfig {
    private const val SEED_SUBDIRECTORY = "seed/"
    const val iconSubdirectory: String = "icons/"
    private const val LOCAL_CONNECTOR_CATALOG_FILE_NAME = "oss_registry.json"
    private const val DEFAULT_LOCAL_CONNECTOR_CATALOG_PATH =
        SEED_SUBDIRECTORY + LOCAL_CONNECTOR_CATALOG_FILE_NAME

    val localConnectorCatalogPath: String
        get() {
            val customCatalogPath = EnvConfigs().localCatalogPath
            if (customCatalogPath.isPresent) {
                return customCatalogPath.get()
            }

            return DEFAULT_LOCAL_CONNECTOR_CATALOG_PATH
        }
}
