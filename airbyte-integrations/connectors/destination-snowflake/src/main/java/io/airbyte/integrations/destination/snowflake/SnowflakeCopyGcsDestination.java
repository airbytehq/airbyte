/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopier;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import javax.sql.DataSource;

public class SnowflakeCopyGcsDestination extends CopyDestination {

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    return CopyConsumerFactory.create(
        outputRecordCollector,
        getDatabase(getDataSource(config)),
        getSqlOperations(),
        getNameTransformer(),
        GcsConfig.getGcsConfig(config),
        catalog,
        new SnowflakeGcsStreamCopierFactory(),
        getConfiguredSchema(config));
  }

  @Override
  public void checkPersistence(final JsonNode config) throws Exception {
    GcsStreamCopier.attemptWriteToPersistence(GcsConfig.getGcsConfig(config));
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new SnowflakeSQLNameTransformer();
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    return SnowflakeDatabase.createDataSource(config);
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return SnowflakeDatabase.getDatabase(dataSource);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new SnowflakeSqlOperations();
  }

  private String getConfiguredSchema(final JsonNode config) {
    return config.get("schema").asText();
  }

}
