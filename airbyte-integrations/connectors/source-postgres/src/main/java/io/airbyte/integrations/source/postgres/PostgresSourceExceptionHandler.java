/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres;

import io.airbyte.cdk.integrations.util.ConnectorErrorProfileBuilder;
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler;
import io.airbyte.cdk.integrations.util.FailureType;
import java.util.ArrayList;
import java.util.Arrays;

public class PostgresSourceExceptionHandler extends ConnectorExceptionHandler {

  private String POSTGRES_RECOVERY_CONNECTION_ERROR_MESSAGE =
      "We're having issues syncing from a Postgres replica that is configured as a hot standby server. " +
          "Please see https://go.airbyte.com/pg-hot-standby-error-message for options and workarounds";

  private String DATABASE_READ_ERROR  = "Encountered an error while reading the database";

  @SuppressWarnings("this-escape")
  public PostgresSourceExceptionHandler() {
    initializeErrorDictionary();
  }

  @Override
  public void initializeErrorDictionary() {
    super.initializeErrorDictionary();
    // A sample translation rule that translates the Postgres temp_file_limit error to a user-friendly message
    this.getConnectorErrorDictionary().add(new ConnectorErrorProfileBuilder()
            .errorClass("Postgres SQL Exception")
            .regexMatchingPattern(".*temporary file size exceeds temp_file_limit.*")
            .failureType(FailureType.TRANSIENT)
            .externalMessage("Encountered an error while reading the database")
            .sampleInternalMessage("org.postgresql.util.PSQLException: ERROR: temporary file size exceeds temp_file_limit")
            .referenceLinks(Arrays.asList("https://github.com/airbytehq/airbyte/issues/27090", "https://github.com/airbytehq/oncall/issues/1822"))
            .build());

    this.getConnectorErrorDictionary().add(
            new ConnectorErrorProfileBuilder()
                    .errorClass("Postgres SQL Exception")
                    .regexMatchingPattern(".*an i/o error occurred while sending to the backend.*")
                    .failureType(FailureType.TRANSIENT)
                    .externalMessage(DATABASE_READ_ERROR)
                    .sampleInternalMessage("org.postgresql.util.PSQLException: An I/O error occured while sending to the backend.")
                    .referenceLinks(new ArrayList<>())
                    .build());

    this.getConnectorErrorDictionary().add(
            new ConnectorErrorProfileBuilder()
                    .errorClass("Postgres Query Conflicts")
                    .regexMatchingPattern(".*due to conflict with recovery.*")
                    .failureType(FailureType.TRANSIENT)
                    .externalMessage(POSTGRES_RECOVERY_CONNECTION_ERROR_MESSAGE)
                    .sampleInternalMessage("ERROR: canceling statement due to conflict with recovery.")
                    .referenceLinks(new ArrayList<>())
                    .build());
  }

}
