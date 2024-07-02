package io.airbyte.integrations.source.mysql;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import io.airbyte.cdk.integrations.util.ConnectorErrorProfile;
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler;


public class MySqlSourceExceptionHandler extends ConnectorExceptionHandler  {

    private  List<ConnectorErrorProfile> connectorErrorDictionary;

    public MySqlSourceExceptionHandler() {
        initializeErrorDictionary();
    }

    private void initializeErrorDictionary() {
        connectorErrorDictionary = new ArrayList<>();
        // A sample translation rule that translates the temp_file_limit error to a user-friendly message
        // The regex pattern ^temp_file_limit$ is used to match the error message
        connectorErrorDictionary.add(
                new ConnectorErrorProfile(
                        "MySQL Syntax Exception",
                        "unknown column '.+' in 'field list'",
                        "config",
                        "A column needed by MySQL source connector is missing in the database",
                        "Unknown column 'X' in 'field list'",
                        new ArrayList<>())
        );

        connectorErrorDictionary.add(
                new ConnectorErrorProfile(
                        "MySQL EOF Exception",
                        "can not read response from server. expected to read [1-9]\\d* bytes",
                        "transient",
                        "Can not read data from MySQL server",
                        "java.io.EOFException: Can not read response from server. " +
                                "Expected to read X bytes, read Y bytes before connection was unexpectedly lost.",
                        new ArrayList<>())
        );

    }

    @Override
    public String translateConnectorSpecificErrorMessage(Throwable e) {
        for (ConnectorErrorProfile errorProfile : connectorErrorDictionary)
            if (e.getMessage().toLowerCase().matches(
                    Objects.requireNonNull(errorProfile.getRegexMatchingPattern())))
                return errorProfile.getExternalMessage();
        return null;
    }

}
