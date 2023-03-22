/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator;
import io.airbyte.integrations.destination.staging.StagingOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.Map;

public abstract class SnowflakeSqlStagingOperations extends SnowflakeSqlOperations implements StagingOperations {

  /**
   * This method is used in Check connection method to make sure that user has the Write permission
   */
  protected void attemptWriteToStage(final String outputSchema,
                                     final String stageName,
                                     final JdbcDatabase database)
      throws Exception {

    final CsvSerializedBuffer csvSerializedBuffer = new CsvSerializedBuffer(
        new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
        new StagingDatabaseCsvSheetGenerator(),
        true);

    // create a dummy stream\records that will bed used to test uploading
    csvSerializedBuffer.accept(new AirbyteRecordMessage()
        .withData(Jsons.jsonNode(Map.of("testKey", "testValue")))
        .withEmittedAt(System.currentTimeMillis()));
    csvSerializedBuffer.flush();

    uploadRecordsToStage(database, csvSerializedBuffer, outputSchema, stageName,
        stageName.endsWith("/") ? stageName : stageName + "/");
  }

}
