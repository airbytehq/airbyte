/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

public class DatabricksDestination extends CopyDestination {

  public DatabricksDestination() {
    super("database_schema");
  }

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new DatabricksDestination()).run(args);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog, Consumer<AirbyteMessage> outputRecordCollector) {
    DatabricksDestinationConfig databricksConfig = DatabricksDestinationConfig.get(config);
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
  public void checkPersistence(JsonNode config) {
    DatabricksDestinationConfig databricksConfig = DatabricksDestinationConfig.get(config);
    S3StreamCopier.attemptS3WriteAndDelete(databricksConfig.getS3DestinationConfig().getS3Config());
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new DatabricksNameTransformer();
  }

  @Override
  public JdbcDatabase getDatabase(JsonNode jsonConfig) {
    return getDatabase(DatabricksDestinationConfig.get(jsonConfig));
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new DatabricksSqlOperations();
  }

  static String getDatabricksConnectionString(DatabricksDestinationConfig databricksConfig) {
    return String.format("jdbc:spark://%s:%s/default;transportMode=http;ssl=1;httpPath=%s;UserAgentEntry=Airbyte",
        databricksConfig.getDatabricksServerHostname(),
        databricksConfig.getDatabricksPort(),
        databricksConfig.getDatabricksHttpPath());
  }

  static JdbcDatabase getDatabase(DatabricksDestinationConfig databricksConfig) {
    return Databases.createJdbcDatabase(
        DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.getDatabricksPersonalAccessToken(),
        getDatabricksConnectionString(databricksConfig),
        DatabricksConstants.DATABRICKS_DRIVER_CLASS);
  }

}
