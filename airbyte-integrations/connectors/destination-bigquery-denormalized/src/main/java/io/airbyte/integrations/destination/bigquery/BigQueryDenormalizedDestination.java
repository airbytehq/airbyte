/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.sentry.ITransaction;
import io.sentry.Sentry;
import io.sentry.SpanStatus;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedDestination extends BigQueryDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedDestination.class);

  public static void initSentry() {
    Sentry.init(options -> {
      // allow setting properties from env variables see
      // https://docs.sentry.io/platforms/java/configuration/
      options.setEnableExternalConfiguration(true);
      // To set a uniform sample rate
      options.setTracesSampleRate(1.0);
    });
    Sentry.configureScope(scope -> {
      scope.setTag("connector", "destination-bigquery-denormalized");
    });
  }

  @Override
  protected String getTargetTableName(final String streamName) {
    // This BigQuery destination does not write to a staging "raw" table but directly to a normalized
    // table
    return getNamingResolver().getIdentifier(streamName);
  }

  @Override
  protected Map<UploaderType, BigQueryRecordFormatter> getFormatterMap(JsonNode jsonSchema) {
    return Map.of(UploaderType.STANDARD, new DefaultBigQueryDenormalizedRecordFormatter(jsonSchema, getNamingResolver()),
        UploaderType.AVRO, new GcsBigQueryDenormalizedRecordFormatter(jsonSchema, getNamingResolver()));
  }

  /**
   * BigQuery might have different structure of the Temporary table. If this method returns TRUE,
   * temporary table will have only three common Airbyte attributes. In case of FALSE, temporary table
   * structure will be in line with Airbyte message JsonSchema.
   *
   * @return use default AirbyteSchema or build using JsonSchema
   */
  @Override
  protected boolean isDefaultAirbyteTmpTableSchema() {
    // Build temporary table structure based on incoming JsonSchema
    return false;
  }

  public static void main(final String[] args) throws Exception {
    initSentry();
    final Destination destination = new BigQueryDenormalizedDestination();
    ITransaction transaction = Sentry.startTransaction("IntegrationRunner()", "run");
    try {
      LOGGER.info("starting destination: {}", BigQueryDestination.class);
      new IntegrationRunner(destination).run(args);
    } catch (Exception e) {
      transaction.setThrowable(e);
      transaction.setStatus(SpanStatus.INTERNAL_ERROR);
    } finally {
      transaction.finish();
      LOGGER.info("completed destination: {}", BigQueryDestination.class);
    }
  }

}
