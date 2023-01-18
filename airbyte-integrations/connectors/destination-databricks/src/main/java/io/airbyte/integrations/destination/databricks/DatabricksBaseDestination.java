/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import javax.sql.DataSource;

public abstract class DatabricksBaseDestination extends CopyDestination {

  public DatabricksBaseDestination() {
    super("database_schema");
  }

  @Override
  public void checkPersistence(JsonNode config) {
    checkPersistence(DatabricksDestinationConfig.get(config).getStorageConfig());
  }

  protected abstract void checkPersistence(DatabricksStorageConfig databricksConfig);

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final DatabricksDestinationConfig databricksConfig = DatabricksDestinationConfig.get(config);
    final DataSource dataSource = getDataSource(config);
    return CopyConsumerFactory.create(
        outputRecordCollector,
        dataSource,
        getDatabase(dataSource),
        getSqlOperations(),
        getNameTransformer(),
        databricksConfig,
        catalog,
        getStreamCopierFactory(),
        databricksConfig.getDatabaseSchema());
  }

  protected abstract DatabricksStreamCopierFactory getStreamCopierFactory();

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new DatabricksNameTransformer();
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    final DatabricksDestinationConfig databricksConfig = DatabricksDestinationConfig.get(config);
    return DataSourceFactory.create(
        DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.getDatabricksPersonalAccessToken(),
        DatabricksConstants.DATABRICKS_DRIVER_CLASS,
        getDatabricksConnectionString(databricksConfig));
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new DatabricksSqlOperations();
  }

  public static String getDatabricksConnectionString(final DatabricksDestinationConfig databricksConfig) {
    return String.format(DatabaseDriver.DATABRICKS.getUrlFormatString(),
        databricksConfig.getDatabricksServerHostname(),
        databricksConfig.getDatabricksHttpPath());
  }

}
