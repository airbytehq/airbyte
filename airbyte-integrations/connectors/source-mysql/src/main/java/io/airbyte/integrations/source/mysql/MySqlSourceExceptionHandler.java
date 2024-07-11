/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mysql;

import io.airbyte.cdk.integrations.util.ConnectorErrorProfileBuilder;
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler;
import io.airbyte.cdk.integrations.util.FailureType;
import java.util.ArrayList;

public class MySqlSourceExceptionHandler extends ConnectorExceptionHandler {

  @SuppressWarnings("this-escape")
  public MySqlSourceExceptionHandler() {
    initializeErrorDictionary();
  }

  @Override
  public void initializeErrorDictionary() {
    add(new ConnectorErrorProfileBuilder()
            .errorClass("MySQL Syntax Exception")
            .regexMatchingPattern(".*unknown column '.+' in 'field list'.*")
            .failureType(FailureType.CONFIG)
            .externalMessage("A column needed by MySQL source connector is missing in the database")
            .sampleInternalMessage("Unknown column 'X' in 'field list'")
            .referenceLinks(new ArrayList<>())
            .build());

    add(new ConnectorErrorProfileBuilder()
            .errorClass("MySQL EOF Exception")
            .regexMatchingPattern(".*can not read response from server. expected to read [1-9]\\d* bytes.*")
            .failureType(FailureType.TRANSIENT)
            .externalMessage("Can not read data from MySQL server")
            .sampleInternalMessage("java.io.EOFException: Can not read response from server. " +
                "Expected to read X bytes, read Y bytes before connection was unexpectedly lost.")
            .referenceLinks(new ArrayList<>())
            .build());
  }

}
