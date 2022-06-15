/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;

public class PostgresUtils {

  private static final String PGOUTPUT_PLUGIN = "pgoutput";

  public static final String CDC_LSN = "_ab_cdc_lsn";

  public static String getPluginValue(final JsonNode field) {
    return field.has("plugin") ? field.get("plugin").asText() : PGOUTPUT_PLUGIN;
  }

}
