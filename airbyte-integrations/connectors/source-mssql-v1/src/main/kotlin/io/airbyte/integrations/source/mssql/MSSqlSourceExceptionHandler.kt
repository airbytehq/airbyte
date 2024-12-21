/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.integrations.util.ConnectorErrorProfile
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler
import io.airbyte.cdk.integrations.util.FailureType

class MSSqlSourceExceptionHandler : ConnectorExceptionHandler() {
    override fun initializeErrorDictionary() {

        val DATABASE_READ_ERROR = "Encountered an error while reading the database, will retry"

        // include common error profiles
        super.initializeErrorDictionary()

        // adding connector specific error profiles
        add(
            ConnectorErrorProfile(
                errorClass = "MS SQL Exception", // which should we use?
                regexMatchingPattern =
                    ".*returned an incomplete response. The connection has been closed.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = DATABASE_READ_ERROR,
                sampleInternalMessage =
                    "com.microsoft.sqlserver.jdbc.SQLServerException: SQL Server returned an incomplete response. The connection has been closed.",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/6623")
            )
        )
    }
}
