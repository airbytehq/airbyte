/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;

public class RedshiftDestinationAcceptanceTestSSL extends RedshiftCopyDestinationAcceptanceTest {

  @Override
  protected JsonNode getConfig() {
    final JsonNode baseConfig = Jsons.clone(getStaticConfig());
    ((ObjectNode) baseConfig).put("tls", true);
    ((ObjectNode) baseConfig).put("schema", Strings.addRandomSuffix("integration_test", "_", 5));
    return baseConfig;
  }

  @Override
  protected Database getDatabase() {
    return Databases.createDatabase(
        getConfig().get("username").asText(),
        getConfig().has("password") ? getConfig().get("password").asText() : null,
        String.format("jdbc:redshift://%s:%s/%s",
            getConfig().get("host").asText(),
            getConfig().get("port").asText(),
            getConfig().get("database").asText()),
        RedshiftInsertDestination.DRIVER_CLASS, null,
        "ssl=true;sslfactory=com.amazon.redshift.ssl.NonValidatingFactory");
  }

}
