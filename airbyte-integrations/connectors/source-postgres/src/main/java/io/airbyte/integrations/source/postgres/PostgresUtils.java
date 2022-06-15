/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;

public class PostgresUtils {

  private static final String PGOUTPUT_PLUGIN = "pgoutput";
  public static final int PG_DEBEZIUM_TIMEOUT_SECONDS = 60;

  public static String getPluginValue(final JsonNode field) {
    return field.has("plugin") ? field.get("plugin").asText() : PGOUTPUT_PLUGIN;
  }

}
