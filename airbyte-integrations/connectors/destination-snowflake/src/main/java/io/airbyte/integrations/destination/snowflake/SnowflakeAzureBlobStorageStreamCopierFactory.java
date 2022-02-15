/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageStreamCopierFactory;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;

public class SnowflakeAzureBlobStorageStreamCopierFactory extends AzureBlobStorageStreamCopierFactory {

  @Override
  public StreamCopier create(String configuredSchema,
                             AzureBlobStorageConfig config,
                             String stagingFolder,
                             ConfiguredAirbyteStream configuredStream,
                             ExtendedNameTransformer nameTransformer,
                             JdbcDatabase db,
                             SqlOperations sqlOperations) {
    return null;
  }

}
