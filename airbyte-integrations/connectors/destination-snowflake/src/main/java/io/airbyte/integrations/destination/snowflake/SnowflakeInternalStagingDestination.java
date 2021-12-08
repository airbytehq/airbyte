/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

public class SnowflakeInternalStagingDestination extends AbstractJdbcDestination implements Destination {

  public SnowflakeInternalStagingDestination() {
    super("", new SnowflakeSQLNameTransformer(), new SnowflakeStagingSqlOperations());
  }

  @Override
  protected JdbcDatabase getDatabase(final JsonNode config) {
    return SnowflakeDatabase.getDatabase(config);
  }

  // this is a no op since we override getDatabase.
  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    return Jsons.emptyObject();
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    return SnowflakeInternalStagingConsumerFactory.create(outputRecordCollector, getDatabase(config),
        new SnowflakeStagingSqlOperations(), new SnowflakeSQLNameTransformer(), config, catalog);
  }

}
