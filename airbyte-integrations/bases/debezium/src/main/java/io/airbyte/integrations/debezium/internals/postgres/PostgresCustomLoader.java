/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.postgres;

import io.airbyte.commons.json.Jsons;
import io.debezium.connector.postgresql.PostgresConnectorConfig;
import io.debezium.connector.postgresql.PostgresOffsetContext;
import io.debezium.connector.postgresql.PostgresOffsetContext.Loader;
import java.util.Collections;
import java.util.Map;

public class PostgresCustomLoader extends Loader {

  private Map<String, ?> offset;

  public PostgresCustomLoader(PostgresConnectorConfig connectorConfig) {
    super(connectorConfig);
  }

  @Override
  public PostgresOffsetContext load(Map<String, ?> offset) {
    this.offset = Jsons.clone(offset);
    return super.load(offset);
  }

  public Map<String, ?> getRawOffset() {
    return Collections.unmodifiableMap(offset);
  }

}
