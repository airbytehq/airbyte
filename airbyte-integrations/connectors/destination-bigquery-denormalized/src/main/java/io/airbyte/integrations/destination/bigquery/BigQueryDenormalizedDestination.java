/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Table;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.arrayformater.LegacyArrayFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryUploaderFactory;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.protocol.models.AirbyteStream;
import java.io.IOException;
import java.util.Map;
import java.util.function.BiFunction;
import java.util.function.Function;
import javax.annotation.Nullable;
import org.apache.avro.Schema;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedDestination extends BigQueryDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedDestination.class);

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

  @Override
  protected void putStreamIntoUploaderMap(AirbyteStream stream, UploaderConfig uploaderConfig,
      Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap) throws IOException {
    Table existingTable = uploaderConfig.getBigQuery().getTable(uploaderConfig.getConfigStream().getStream().getNamespace(), uploaderConfig.getTargetTableName());
    BigQueryRecordFormatter formatter = uploaderConfig.getFormatter();

    if (existingTable != null)
    {
      LOGGER.info("Target table already exists. Checking could we use the modern destination processing.");
      if (!compareSchemas((formatter.getBigQuerySchema()), existingTable.getDefinition().getSchema())) {
        ((DefaultBigQueryDenormalizedRecordFormatter) formatter).setArrayFormatter(new LegacyArrayFormatter());
        LOGGER.warn("Existing target table has different structure with the new destination processing. Trying old implementation.");
      } else {
        LOGGER.info("Existing target table {} has equal structure with the destination schema. Using the new array processing.", stream.getName());
      }
    } else {
      LOGGER.info("Target table is not created yet. The modern destination processing will be used.");
    }

    AbstractBigQueryUploader<?> uploader = BigQueryUploaderFactory.getUploader(uploaderConfig);
    uploaderMap.put(
        AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream),
        uploader);
  }

  /**
   * Compare calculated bigquery schema and existing schema of the table.
   * Note! We compare only fields from the calculated schema to avoid manually created fields in the table.
   * @param expectedSchema BigQuery schema of the table which we calculated using the stream schema config
   * @param existingSchema BigQuery schema of the existing table (created by previous run)
   * @return               Are calculated fields same as we have in the existing table
   */
  private boolean compareSchemas(com.google.cloud.bigquery.Schema expectedSchema, @Nullable com.google.cloud.bigquery.Schema existingSchema) {
    LOGGER.error("Comparing schemas \nexpected: {} \nvs \nexisting: {}", existingSchema, existingSchema);
    if (expectedSchema != null && existingSchema == null) {
      LOGGER.warn("Existing schema is null when we expect {}", expectedSchema);
      return false;
    } else if (expectedSchema == null && existingSchema == null) {
      LOGGER.info("Existing and expected schemas are null.");
      return true;
    } else if (expectedSchema == null) {
      LOGGER.warn("Expected schema is null when we have existing schema {}", existingSchema);
      return false;
    }

    var expectedFields = expectedSchema.getFields();
    var existingFields = existingSchema.getFields();

    for (Field expectedField : expectedFields) {
      LOGGER.error("Comparing \nfields: {} \nvs \nexisting: {}", existingSchema, existingSchema);
      var existingField = existingFields.get(expectedField.getName());
      if (!expectedField.equals(existingField)) {
        LOGGER.warn("Expected field {} is different from existing field {}", expectedField, existingField);
        return false;
      }
    }

    LOGGER.info("Existing and expected schemas are equal.");
    return true;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BigQueryDenormalizedDestination();
    new IntegrationRunner(destination).run(args);
  }

}
