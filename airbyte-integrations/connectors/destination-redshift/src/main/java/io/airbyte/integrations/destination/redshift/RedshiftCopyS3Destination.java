/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.getJdbcDatabase;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopyConfig;
import io.airbyte.integrations.destination.s3.S3Destination;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

/**
 * A more efficient Redshift Destination than the sql-based {@link RedshiftDestination}. Instead of
 * inserting data as batched SQL INSERTs, we follow Redshift best practices and, 1) Stream the data
 * to S3, creating multiple compressed files per stream. 2) Create a manifest file to load the data
 * files in parallel. See:
 * https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-use-copy.html for more info.
 * <p>
 * Creating multiple files per stream currently has the naive approach of one file per batch on a
 * stream up to the max limit of (26 * 26 * 26) 17576 files. Each batch is randomly prefixed by 3
 * Alpha characters and on a collision the batch is appended to the existing file.
 */
public class RedshiftCopyS3Destination extends CopyDestination {

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return CopyConsumerFactory.create(
        outputRecordCollector,
        getDatabase(config),
        getSqlOperations(),
        getNameTransformer(),
        S3CopyConfig.getS3CopyConfig(config),
        catalog,
        new RedshiftStreamCopierFactory(),
        getConfiguredSchema(config));
  }

  @Override
  public void checkPersistence(final JsonNode config) throws Exception {
    S3Destination.attemptS3WriteAndDelete(getS3DestinationConfig(config), "");
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new RedshiftSQLNameTransformer();
  }

  @Override
  public JdbcDatabase getDatabase(final JsonNode config) {
    return getJdbcDatabase(config);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new RedshiftSqlOperations();
  }

  private String getConfiguredSchema(final JsonNode config) {
    return config.get("schema").asText();
  }

  private S3DestinationConfig getS3DestinationConfig(final JsonNode config) {
    return S3DestinationConfig.getS3DestinationConfig(config);
  }

}
