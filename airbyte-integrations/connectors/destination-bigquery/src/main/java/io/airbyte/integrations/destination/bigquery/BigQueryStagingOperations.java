/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import java.util.List;

/**
 * This interface is similar to
 * {@link io.airbyte.integrations.destination.s3.BlobStorageOperations}.
 *
 * <p>
 * Similar interface to {@link io.airbyte.integrations.destination.jdbc.SqlOperations}
 * </p>
 */
public interface BigQueryStagingOperations {

  String getStagingFullPath(final String datasetId, final String stream);

  /**
   * Create a schema with provided name if it does not already exist
   *
   * @param datasetId Name of schema
   * @param datasetLocation Location of where the dataset exists (e.g. US, EU, Asia Pacific)
   */
  void createSchemaIfNotExists(final String datasetId, final String datasetLocation);

  /**
   * Create a table with provided tableId in provided schema if it does not already exist
   *
   * @param tableId Name of table
   * @param tableSchema Schema of the data being synced
   */
  void createTableIfNotExists(final TableId tableId, final Schema tableSchema);

  /**
   * Create a staging folder with provided stream to upload temporary files before loading into the
   * final destination
   *
   * @param datasetId Name of schema
   * @param stream Name of stream (e.g. API source or database table)
   */
  void createStageIfNotExists(final String datasetId, final String stream);

  String uploadRecordsToStage(final String datasetId, final String stream, final SerializableBuffer writer) throws Exception;

  /**
   * Copies data from staging area to the target table
   *
   * @param datasetId Name of schema
   * @param stream Name of stream
   * @param tableId Name of destination's target table
   * @param schema Schema of the data being synced
   * @param stagedFiles collection of staged files
   * @throws Exception
   */
  void copyIntoTableFromStage(final String datasetId,
                                    final String stream,
                                    final TableId tableId,
                                    final Schema schema,
                                    final List<String> stagedFiles)
      throws Exception;

  /**
   * This method was primarily used to clean up staging area at the end of a sync, however, since we're
   * no longer trying to commit remaining staged files at the end of a sync this is super-ceded by
   * #dropStageIfExists
   */
  @Deprecated
  void cleanUpStage(final String datasetId, final String stream, final List<String> stagedFiles);


  void dropTableIfExists(final String datasetId, final TableId tableId);

  void dropStageIfExists(final String datasetId, final String stream);

  void truncateTableIfExists(final String datasetId, final TableId tableId, Schema schema);

}
