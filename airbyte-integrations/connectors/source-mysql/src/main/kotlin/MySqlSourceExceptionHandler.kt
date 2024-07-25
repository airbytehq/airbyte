/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.integrations.util.ConnectorErrorProfile
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler
import io.airbyte.cdk.integrations.util.FailureType

class MySqlSourceExceptionHandler : ConnectorExceptionHandler() {
    override fun initializeErrorDictionary() {
        // adding common error profiles
        super.initializeErrorDictionary()
        // adding connector specific error profiles
        add(
            ConnectorErrorProfile(
                errorClass = "MySQL Syntax Exception",
                regexMatchingPattern = ".*unknown column '.+' in 'field list'.*",
                failureType = FailureType.CONFIG,
                externalMessage =
                    "A column needed by MySQL source connector is missing in the database",
                sampleInternalMessage = "Unknown column 'X' in 'field list'"
            )
        )

        add(
            ConnectorErrorProfile(
                errorClass = "MySQL EOF Exception",
                regexMatchingPattern =
                    ".*can not read response from server. expected to read [1-9]\\d* bytes.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = "Can not read data from MySQL server",
                sampleInternalMessage =
                    "java.io.EOFException: Can not read response from server. Expected to read X bytes, read Y bytes before connection was unexpectedly lost."
            )
        )
    }
}
