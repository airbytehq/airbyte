/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig.getAzureBlobConfig;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageStreamCopier;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import javax.sql.DataSource;

public class SnowflakeCopyAzureBlobStorageDestination extends CopyDestination {

  private final String airbyteEnvironment;

  public SnowflakeCopyAzureBlobStorageDestination(final String airbyteEnvironment) {
    this.airbyteEnvironment = airbyteEnvironment;
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final DataSource dataSource = getDataSource(config);
    return CopyConsumerFactory.create(
        outputRecordCollector,
        dataSource,
        getDatabase(dataSource),
        getSqlOperations(),
        getNameTransformer(),
        getAzureBlobConfig(config.get("loading_method")),
        catalog,
        new SnowflakeAzureBlobStorageStreamCopierFactory(),
        getConfiguredSchema(config));
  }

  @Override
  public void checkPersistence(final JsonNode config) {
    AzureBlobStorageStreamCopier.attemptAzureBlobWriteAndDelete(getAzureBlobConfig(config.get("loading_method")));
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new SnowflakeSQLNameTransformer();
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    return SnowflakeDatabase.createDataSource(config, airbyteEnvironment);
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return SnowflakeDatabase.getDatabase(dataSource);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new SnowflakeSqlOperations();
  }

  @Override
  protected void performCreateInsertTestOnDestination(final String outputSchema,
                                                      final JdbcDatabase database,
                                                      final NamingConventionTransformer nameTransformer)
      throws Exception {
    AbstractJdbcDestination.attemptTableOperations(outputSchema, database, nameTransformer,
        getSqlOperations(), true);
  }

  private String getConfiguredSchema(final JsonNode config) {
    return config.get("schema").asText();
  }

}
