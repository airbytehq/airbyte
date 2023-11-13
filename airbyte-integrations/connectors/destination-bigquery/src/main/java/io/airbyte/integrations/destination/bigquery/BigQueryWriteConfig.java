/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableId;
import io.airbyte.protocol.models.v0.DestinationSyncMode;

/**
 * @param streamName output stream name
 * @param namespace
 * @param datasetId the dataset ID is equivalent to output schema
 * @param datasetLocation location of dataset (e.g. US, EU)
 * @param tmpTableId BigQuery temporary table
 * @param targetTableId BigQuery final raw table
 * @param tableSchema schema for the table
 * @param syncMode BigQuery's mapping of write modes to Airbyte's sync mode
 */
public record BigQueryWriteConfig(
                                  String streamName,
                                  String namespace,
                                  String datasetId,
                                  String datasetLocation,
                                  TableId tmpTableId,
                                  TableId targetTableId,
                                  Schema tableSchema,
                                  DestinationSyncMode syncMode) {

  public BigQueryWriteConfig(final String streamName,
                             final String namespace,
                             final String datasetId,
                             final String datasetLocation,
                             final String tmpTableName,
                             final String targetTableName,
                             final Schema tableSchema,
                             final DestinationSyncMode syncMode) {
    this(
        streamName,
        namespace,
        datasetId,
        datasetLocation,
        TableId.of(datasetId, tmpTableName),
        TableId.of(datasetId, targetTableName),
        tableSchema,
        syncMode);
  }

}
