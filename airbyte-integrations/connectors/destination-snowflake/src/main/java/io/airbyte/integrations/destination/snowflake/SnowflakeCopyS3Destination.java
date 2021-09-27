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
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

public class SnowflakeCopyS3Destination extends CopyDestination {

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog catalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    return CopyConsumerFactory.create(
        outputRecordCollector,
        getDatabase(config),
        getSqlOperations(),
        getNameTransformer(),
        getS3Config(config),
        catalog,
        new SnowflakeS3StreamCopierFactory(),
        getConfiguredSchema(config));
  }

  @Override
  public void checkPersistence(JsonNode config) {
    S3StreamCopier.attemptS3WriteAndDelete(getS3Config(config));
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new SnowflakeSQLNameTransformer();
  }

  @Override
  public JdbcDatabase getDatabase(JsonNode config) {
    return SnowflakeDatabase.getDatabase(config);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new SnowflakeSqlOperations();
  }

  private String getConfiguredSchema(JsonNode config) {
    return config.get("schema").asText();
  }

  private S3Config getS3Config(JsonNode config) {
    final JsonNode loadingMethod = config.get("loading_method");
    return S3Config.getS3Config(loadingMethod);
  }

}
