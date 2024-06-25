/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres;


import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import io.airbyte.cdk.integrations.util.ConnectorErrorProfile;
import io.airbyte.cdk.integrations.util.ConnectorExceptionTranslator;

public class PostgresSourceExceptionTranslator extends ConnectorExceptionTranslator {

    String POSTGRES_RECOVERY_CONNECTION_ERROR_MESSAGE =
            "We're having issues syncing from a Postgres replica that is configured as a hot standby server. " +
            "Please see https://go.airbyte.com/pg-hot-standby-error-message for options and workarounds";

    private  List<ConnectorErrorProfile> connectorErrorDictionary;

    public PostgresSourceExceptionTranslator() {
        initializeErrorDictionary();
    }

    private void initializeErrorDictionary() {
        connectorErrorDictionary = new ArrayList<>();
        // A sample translation rule that translates the temp_file_limit error to a user-friendly message
        // The regex pattern ^temp_file_limit$ is used to match the error message
        connectorErrorDictionary.add(
                new ConnectorErrorProfile(
                        "Postgres SQL Exception",
                "temporary file size exceeds temp_file_limit",
                        "transient",
                        this.DATABASE_READ_ERROR,
                "org.postgresql.util.PSQLException: ERROR: temporary file size exceeds temp_file_limit",
                        Arrays.asList("https://github.com/airbytehq/airbyte/issues/27090",
                                "https://github.com/airbytehq/oncall/issues/1822"))
        );

        connectorErrorDictionary.add(
                new ConnectorErrorProfile(
                        "Postgres  SQL Exception",
                        "an i/o error occurred while sending to the backend",
                        "transient",
                        this.DATABASE_READ_ERROR,
                        "org.postgresql.util.PSQLException: An I/O error occured while sending to the backend.",
                        new ArrayList<>())
        );

        connectorErrorDictionary.add(
                new ConnectorErrorProfile(
                        "Postgres Query Conflicts",
                        "due to conflict with recovery",
                        "transient",
                        this.POSTGRES_RECOVERY_CONNECTION_ERROR_MESSAGE,
                        "ERROR: canceling statement due to conflict with recovery.",
                        new ArrayList<>())
        );
    }

    @Override
    public String translateConnectorSpecificErrorMessage(Throwable e) {
        for (ConnectorErrorProfile errorProfile : connectorErrorDictionary)
            if (e.getMessage().toLowerCase().matches(errorProfile.getRegexMatchingPattern()))
                return errorProfile.getExternalMessage();
        return null;
    }

}
