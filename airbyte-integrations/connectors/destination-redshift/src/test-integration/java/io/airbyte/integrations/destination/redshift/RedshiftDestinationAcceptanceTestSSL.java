/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import io.airbyte.db.Database;
import io.airbyte.db.Databases;

public class RedshiftDestinationAcceptanceTestSSL extends RedshiftCopyDestinationAcceptanceTest {

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
