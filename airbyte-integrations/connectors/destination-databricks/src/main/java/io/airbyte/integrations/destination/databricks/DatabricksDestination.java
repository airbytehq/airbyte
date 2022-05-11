/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.s3.S3Destination;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

public class DatabricksDestination extends CopyDestination {

  public DatabricksDestination() {
    super("database_schema");
  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new DatabricksDestination()).run(args);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final DatabricksDestinationConfig databricksConfig = DatabricksDestinationConfig.get(config);
    return CopyConsumerFactory.create(
        outputRecordCollector,
        getDatabase(config),
        getSqlOperations(),
        getNameTransformer(),
        databricksConfig,
        catalog,
        new DatabricksStreamCopierFactory(),
        databricksConfig.getDatabaseSchema());
  }

  @Override
  public void checkPersistence(final JsonNode config) {
    final DatabricksDestinationConfig databricksConfig = DatabricksDestinationConfig.get(config);
    final S3DestinationConfig s3Config = databricksConfig.getS3DestinationConfig();
    S3Destination.attemptS3WriteAndDelete(new S3StorageOperations(getNameTransformer(), s3Config.getS3Client(), s3Config), s3Config, "");
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new DatabricksNameTransformer();
  }

  @Override
  public JdbcDatabase getDatabase(final JsonNode jsonConfig) {
    return getDatabase(DatabricksDestinationConfig.get(jsonConfig));
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new DatabricksSqlOperations();
  }

  static String getDatabricksConnectionString(final DatabricksDestinationConfig databricksConfig) {
    return String.format("jdbc:spark://%s:%s/default;transportMode=http;ssl=1;httpPath=%s;UserAgentEntry=Airbyte",
        databricksConfig.getDatabricksServerHostname(),
        databricksConfig.getDatabricksPort(),
        databricksConfig.getDatabricksHttpPath());
  }

  static JdbcDatabase getDatabase(final DatabricksDestinationConfig databricksConfig) {
    return new DefaultJdbcDatabase(DataSourceFactory.create(
        DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.getDatabricksPersonalAccessToken(),
        DatabricksConstants.DATABRICKS_DRIVER_CLASS,
        getDatabricksConnectionString(databricksConfig)
      )
    );
  }

}
