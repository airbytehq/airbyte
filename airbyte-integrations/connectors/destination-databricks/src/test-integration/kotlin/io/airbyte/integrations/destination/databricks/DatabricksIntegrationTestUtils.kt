/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks

import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import java.nio.file.Path

object DatabricksIntegrationTestUtils {
    const val OAUTH_CONFIG_PATH = "secrets/oauth_config.json"
    val oauthConfigJson = Jsons.deserialize(IOs.readFile(Path.of(OAUTH_CONFIG_PATH)))
    val oauthConfig = DatabricksConnectorConfig.deserialize(oauthConfigJson)
}
