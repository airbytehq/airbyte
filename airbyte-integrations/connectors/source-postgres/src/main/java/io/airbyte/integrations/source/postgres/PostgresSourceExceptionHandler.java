/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres;

import io.airbyte.cdk.integrations.util.ConnectorErrorProfile;
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler;
import io.airbyte.cdk.integrations.util.FailureType;
import java.util.ArrayList;
import java.util.Arrays;

public class PostgresSourceExceptionHandler extends ConnectorExceptionHandler {

  String POSTGRES_RECOVERY_CONNECTION_ERROR_MESSAGE =
      "We're having issues syncing from a Postgres replica that is configured as a hot standby server. " +
          "Please see https://go.airbyte.com/pg-hot-standby-error-message for options and workarounds";

  @Override
  public void initializeErrorDictionary() {
    super.initializeErrorDictionary();
    // A sample translation rule that translates the temp_file_limit error to a user-friendly message
    // The regex pattern ^temp_file_limit$ is used to match the error message
    this.getConnectorErrorDictionary().add(
        new ConnectorErrorProfile(
            "Postgres SQL Exception",
            ".*temporary file size exceeds temp_file_limit.*",
            FailureType.TRANSIENT,
            this.DATABASE_READ_ERROR,
            "org.postgresql.util.PSQLException: ERROR: temporary file size exceeds temp_file_limit",
            Arrays.asList("https://github.com/airbytehq/airbyte/issues/27090",
                "https://github.com/airbytehq/oncall/issues/1822")));

    this.getConnectorErrorDictionary().add(
        new ConnectorErrorProfile(
            "Postgres  SQL Exception",
            ".*an i/o error occurred while sending to the backend.*",
            FailureType.TRANSIENT,
            this.DATABASE_READ_ERROR,
            "org.postgresql.util.PSQLException: An I/O error occured while sending to the backend.",
            new ArrayList<>()));

    this.getConnectorErrorDictionary().add(
        new ConnectorErrorProfile(
            "Postgres Query Conflicts",
            ".*due to conflict with recovery.*",
            FailureType.TRANSIENT,
            this.POSTGRES_RECOVERY_CONNECTION_ERROR_MESSAGE,
            "ERROR: canceling statement due to conflict with recovery.",
            new ArrayList<>()));
  }

}
