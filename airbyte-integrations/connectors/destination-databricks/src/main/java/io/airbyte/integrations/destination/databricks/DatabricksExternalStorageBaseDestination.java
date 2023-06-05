/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static io.airbyte.integrations.destination.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.databricks.utils.DatabricksDatabaseUtil;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import javax.sql.DataSource;

public abstract class DatabricksExternalStorageBaseDestination extends CopyDestination {

  public DatabricksExternalStorageBaseDestination() {
    super(DATABRICKS_SCHEMA_KEY);
  }

  @Override
  public void checkPersistence(JsonNode config) {
    checkPersistence(DatabricksDestinationConfig.get(config).storageConfig());
  }

  protected abstract void checkPersistence(DatabricksStorageConfigProvider databricksConfig);

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
        databricksConfig.schema());
  }

  protected abstract DatabricksStreamCopierFactory getStreamCopierFactory();

  @Override
  public StandardNameTransformer getNameTransformer() {
    return new DatabricksNameTransformer();
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    return DatabricksDatabaseUtil.getDataSource(config);
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new DatabricksSqlOperations();
  }

}
