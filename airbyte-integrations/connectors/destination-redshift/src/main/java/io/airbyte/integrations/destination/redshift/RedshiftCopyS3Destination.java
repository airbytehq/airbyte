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
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

/**
 * A more efficient Redshift Destination than the sql-based {@link RedshiftDestination}. Instead of
 * inserting data as batched SQL INSERTs, we follow Redshift best practices and, 1) Stream the data
 * to S3, creating multiple compressed files per stream. 2) Create a manifest file to load the data
 * files in parallel. See:
 * https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-use-copy.html for more info.
 *
 * Creating multiple files per stream currently has the naive approach of one file per batch on a
 * stream up to the max limit of (26 * 26 * 26) 17576 files.  Each batch is randomly prefixed by
 * 3 Alpha characters and on a collision the batch is appended to the existing file.
 */
public class RedshiftCopyS3Destination extends CopyDestination {

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog catalog,
                                            Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return CopyConsumerFactory.create(
        outputRecordCollector,
        getDatabase(config),
        getSqlOperations(),
        getNameTransformer(),
        getS3Config(config),
        catalog,
        new RedshiftStreamCopierFactory(),
        getConfiguredSchema(config));
  }

  @Override
  public void checkPersistence(JsonNode config) throws Exception {
    S3StreamCopier.attemptS3WriteAndDelete(getS3Config(config));
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new RedshiftSQLNameTransformer();
  }

  @Override
  public JdbcDatabase getDatabase(JsonNode config) {
    return getJdbcDatabase(config);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new RedshiftSqlOperations();
  }

  private String getConfiguredSchema(JsonNode config) {
    return config.get("schema").asText();
  }

  private S3Config getS3Config(JsonNode config) {
    return S3Config.getS3Config(config);
  }

}
