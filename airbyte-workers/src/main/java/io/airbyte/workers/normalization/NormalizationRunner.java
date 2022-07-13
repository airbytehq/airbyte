/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.normalization;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.util.stream.Stream;

public interface NormalizationRunner extends AutoCloseable {

  /**
   * After this method is called, the caller must call close. Previous to this method being called a
   * NormalizationRunner can be instantiated and not worry about close being called.
   *
   * @throws Exception - any exception thrown from normalization will be handled gracefully by the
   *         caller.
   */
  default void start() throws Exception {
    // no-op.
  }

  /**
   * Prepare a configured folder to run dbt commands from (similar to what is required by
   * normalization models) However, this does not run the normalization file generation process or dbt
   * at all. This is pulling files from a distant git repository instead of the dbt-project-template.
   *
   * @return true if configuration succeeded. otherwise false.
   * @throws Exception - any exception thrown from configuration will be handled gracefully by the
   *         caller.
   */
  boolean configureDbt(String jobId,
                       int attempt,
                       Path jobRoot,
                       JsonNode config,
                       ResourceRequirements resourceRequirements,
                       OperatorDbt dbtConfig)
      throws Exception;

  /**
   * Executes normalization of the data in the destination.
   *
   * @param jobId - id of the job that launched normalization
   * @param attempt - current attempt
   * @param jobRoot - root dir available for the runner to use.
   * @param config - configuration for connecting to the destination
   * @param catalog - the schema of the json blob in the destination. it is used normalize the blob
   *        into typed columns.
   * @param resourceRequirements
   * @return true of normalization succeeded. otherwise false.
   * @throws Exception - any exception thrown from normalization will be handled gracefully by the
   *         caller.
   */
  boolean normalize(String jobId,
                    int attempt,
                    Path jobRoot,
                    JsonNode config,
                    ConfiguredAirbyteCatalog catalog,
                    ResourceRequirements resourceRequirements)
      throws Exception;

  Stream<AirbyteTraceMessage> getTraceMessages();

}
