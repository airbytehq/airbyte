/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import java.util.Map;
import java.util.function.BiFunction;
import java.util.function.Function;
import org.apache.avro.Schema;

public class BigQueryDenormalizedDestination extends BigQueryDestination {

  @Override
  protected String getTargetTableName(final String streamName) {
    // This BigQuery destination does not write to a staging "raw" table but directly to a normalized
    // table
    return namingResolver.getIdentifier(streamName);
  }

  @Override
  protected Map<UploaderType, BigQueryRecordFormatter> getFormatterMap(final JsonNode jsonSchema) {
    return Map.of(UploaderType.STANDARD, new DefaultBigQueryDenormalizedRecordFormatter(jsonSchema, namingResolver),
        UploaderType.AVRO, new GcsBigQueryDenormalizedRecordFormatter(jsonSchema, namingResolver));
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

  @Override
  protected BiFunction<BigQueryRecordFormatter, AirbyteStreamNameNamespacePair, Schema> getAvroSchemaCreator() {
    // the json schema needs to be processed by the record former to denormalize
    return (formatter, pair) -> new JsonToAvroSchemaConverter().getAvroSchema(formatter.getJsonSchema(), pair.getName(),
        pair.getNamespace(), true, false, false, true);
  }

  @Override
  protected Function<JsonNode, BigQueryRecordFormatter> getRecordFormatterCreator(final BigQuerySQLNameTransformer namingResolver) {
    return streamSchema -> new GcsBigQueryDenormalizedRecordFormatter(streamSchema, namingResolver);
  }

  /**
   * This BigQuery destination does not write to a staging "raw" table but directly to a normalized
   * table.
   */
  @Override
  protected Function<String, String> getTargetTableNameTransformer(final BigQuerySQLNameTransformer namingResolver) {
    return namingResolver::getIdentifier;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BigQueryDenormalizedDestination();
    new IntegrationRunner(destination).run(args);
  }

}
