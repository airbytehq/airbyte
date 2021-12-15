/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Field.Builder;
import com.google.cloud.bigquery.Field.Mode;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedDestination extends BigQueryDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedDestination.class);

  @Override
  protected String getTargetTableName(final String streamName) {
    // This BigQuery destination does not write to a staging "raw" table but directly to a normalized
    // table
    return getNamingResolver().getIdentifier(streamName);
  }

  @Override
  protected Map<UploaderType, BigQueryRecordFormatter> getFormatterMap(JsonNode jsonSchema) {
    Map<UploaderType, BigQueryRecordFormatter> formatterMap = new HashMap<>();
    formatterMap.put(UploaderType.STANDARD, new DefaultBigQueryDenormalizedRecordFormatter(jsonSchema, getNamingResolver()));
    formatterMap.put(UploaderType.AVRO, new GcsBigQueryDenormalizedRecordFormatter(jsonSchema, getNamingResolver()));
    return formatterMap;  }

  @Override
  protected boolean isDefaultAirbyteTmpTableSchema() {
    // Use source schema instead of
    return false;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BigQueryDenormalizedDestination();
    LOGGER.info("starting destination: {}", BigQueryDenormalizedDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", BigQueryDenormalizedDestination.class);
  }

}
