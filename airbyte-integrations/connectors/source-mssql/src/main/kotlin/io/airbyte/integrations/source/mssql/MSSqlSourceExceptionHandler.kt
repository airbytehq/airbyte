/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.integrations.util.ConnectorErrorProfile
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler
import io.airbyte.cdk.integrations.util.FailureType

class MSSqlSourceExceptionHandler : ConnectorExceptionHandler() {
    override fun initializeErrorDictionary() {

        // include common error profiles
        super.initializeErrorDictionary()

        // adding connector specific error profiles
        add(
            ConnectorErrorProfile(
                errorClass = "MSSQL Exception",
                regexMatchingPattern =
                    "(?i).*returned an incomplete response. The connection has been closed.*",
                failureType = FailureType.TRANSIENT,
                externalMessage =
                    "(?i).*returned an incomplete response. The connection has been closed.*",
                sampleInternalMessage =
                    "com.microsoft.sqlserver.jdbc.SQLServerException: SQL Server returned an incomplete response. The connection has been closed.",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/6623")
            ),
        )
        add(
            ConnectorErrorProfile(
                errorClass = "MSSQL Exception",
                regexMatchingPattern =
                    "(?i).*SQL Server did not return a response. The connection has been closed.*",
                failureType = FailureType.TRANSIENT,
                externalMessage =
                    "Encountered an error while reading from the database, will retry",
                sampleInternalMessage =
                    "com.microsoft.sqlserver.jdbc.SQLServerException: SQL Server did not return a response. The connection has been closed.",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/7757")
            ),
        )
        add(
            ConnectorErrorProfile(
                errorClass = "MSSQL Exception",
                regexMatchingPattern = "(?i).*The connection is closed.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = "The SQL Server connection was unexpectedly closed, will retry.",
                sampleInternalMessage =
                    "com.microsoft.sqlserver.jdbc.SQLServerException: The connection is closed.",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/6438")
            ),
        )
        add(
            // Error 1205
            // https://learn.microsoft.com/en-us/sql/relational-databases/errors-events/mssqlserver-1205-database-engine-error
            ConnectorErrorProfile(
                errorClass = "MSSQL Exception",
                regexMatchingPattern =
                    "(?i).*was deadlocked on lock resources with another process and has been chosen as the deadlock victim. Rerun the transaction.*",
                failureType = FailureType.TRANSIENT,
                externalMessage =
                    "Transaction conflicted with another process and was terminated, will retry.",
                sampleInternalMessage =
                    "com.microsoft.sqlserver.jdbc.SQLServerException: " +
                        "Transaction (Process ID 63) was deadlocked on lock resources with another process and has been chosen as the deadlock victim. Rerun the transaction.",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/6287")
            ),
        )
        // This error occurs when Debezium encounters an exception.
        // We classify it as TRANSIENT since it may be resolved through automatic retries but can
        // also require investigation and manual intervention.
        add(
            ConnectorErrorProfile(
                errorClass = "Connect Exception",
                regexMatchingPattern = "(?i).*exception occurred in the change event producer.*",
                failureType = FailureType.TRANSIENT,
                externalMessage =
                    "The sync encountered an unexpected error in the change event producer and has stopped. Please check the logs for details and troubleshoot accordingly.",
                sampleInternalMessage =
                    "java.lang.RuntimeException: org.apache.kafka.connect.errors.ConnectException: " +
                        "An exception occurred in the change event producer. This connector will be stopped.",
                referenceLinks =
                    listOf(
                        "https://docs.oracle.com/javase/9/docs/api/java/lang/RuntimeException.html"
                    )
            ),
        )
    }
}
