/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.util.List;

/**
 * This interface is similar to
 * {@link io.airbyte.integrations.destination.s3.BlobStorageOperations}.
 */
public interface BigQueryStagingOperations {

  String getStagingFullPath(final String datasetId, final String stream);

  void createSchemaIfNotExists(final String datasetId, final String datasetLocation);

  void createTmpTableIfNotExists(final TableId tmpTableId, final Schema tableSchema);

  void createStageIfNotExists(final String datasetId, final String stream);

  String uploadRecordsToStage(final String datasetId, final String stream, final SerializableBuffer writer) throws Exception;

  void copyIntoTmpTableFromStage(final String datasetId,
                                 final String stream,
                                 final TableId tmpTableId,
                                 final Schema schema,
                                 final List<String> stagedFiles)
      throws Exception;

  void cleanUpStage(final String datasetId, final String stream, final List<String> stagedFiles);

  void copyIntoTargetTable(final String datasetId,
                           final TableId tmpTableId,
                           final TableId targetTableId,
                           final Schema schema,
                           final DestinationSyncMode syncMode);

  void dropTableIfExists(final String datasetId, final TableId tmpTableId);

  void dropStageIfExists(final String datasetId, final String stream);

}
