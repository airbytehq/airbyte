/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mysql;

import io.airbyte.cdk.integrations.util.ConnectorErrorProfile;
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler;
import io.airbyte.cdk.integrations.util.FailureType;
import java.util.ArrayList;

public class MySqlSourceExceptionHandler extends ConnectorExceptionHandler {

  @Override
  public void initializeErrorDictionary() {
    super.initializeErrorDictionary();
    // A sample translation rule that translates the temp_file_limit error to a user-friendly message
    // The regex pattern ^temp_file_limit$ is used to match the error message
    this.getConnectorErrorDictionary().add(
        new ConnectorErrorProfile(
            "MySQL Syntax Exception",
            ".*unknown column '.+' in 'field list'.*",
            FailureType.CONFIG,
            "A column needed by MySQL source connector is missing in the database",
            "Unknown column 'X' in 'field list'",
            new ArrayList<>()));

    this.getConnectorErrorDictionary().add(
        new ConnectorErrorProfile(
            "MySQL EOF Exception",
            ".*can not read response from server. expected to read [1-9]\\d* bytes.*",
            FailureType.TRANSIENT,
            "Can not read data from MySQL server",
            "java.io.EOFException: Can not read response from server. " +
                "Expected to read X bytes, read Y bytes before connection was unexpectedly lost.",
            new ArrayList<>()));

  }

}
