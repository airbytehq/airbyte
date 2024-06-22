/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres;


import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import io.airbyte.cdk.integrations.util.ConnectorErrorProfile;
import io.airbyte.cdk.integrations.util.ConnectorExceptionTranslator;
import static io.airbyte.cdk.integrations.util.ConnectorExceptionUtil.DATABASE_CONNECTION_ERROR;

public class PostgresExceptionTranslator extends ConnectorExceptionTranslator {
    private  List<ConnectorErrorProfile> connectorErrorDictionary;

    @Override
    public void initializeErrorDictionary() {
        connectorErrorDictionary = new ArrayList<>();
        // A sample translation rule that translates the temp_file_limit error to a user-friendly message
        // The regex pattern ^temp_file_limit$ is used to match the error message
        connectorErrorDictionary.add(
                new ConnectorErrorProfile(1,
                        "Postgres temp file error",
                "\"^temp_file_limit$\"",
                        "System",
                        DATABASE_CONNECTION_ERROR,
                "org.postgresql.util.PSQLException: ERROR: temporary file size exceeds temp_file_limit",
                        Arrays.asList("https://github.com/airbytehq/airbyte/issues/27090",
                                "https://github.com/airbytehq/oncall/issues/1822"))
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
