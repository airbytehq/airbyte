/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeInsertDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDestination.class);

  public SnowflakeInsertDestination() {
    // the driver class is a no op because we override getDatabase.
    super("", new SnowflakeSQLNameTransformer(), new SnowflakeSqlOperations());
  }

  @Override
  protected JdbcDatabase getDatabase(JsonNode config) {
    return SnowflakeDatabase.getDatabase(config);
  }

  // this is a no op since we override getDatabase.
  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    return Jsons.emptyObject();
  }

}
