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
                sampleInternalMessage = "Unknown column 'X' in 'field list'",
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "MySQL EOF Exception",
                regexMatchingPattern =
                    ".*can not read response from server. expected to read [1-9]\\d* bytes.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = "Can not read data from MySQL server",
                sampleInternalMessage =
                    "java.io.EOFException: Can not read response from server. Expected to read X bytes, read Y bytes before connection was unexpectedly lost.",
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "MySQL Hikari Connection Error",
                regexMatchingPattern = ".*connection is not available, request timed out after*",
                failureType = FailureType.TRANSIENT,
                externalMessage = "Database read failed due to connection timeout, will retry.",
                sampleInternalMessage =
                    "java.sql.SQLTransientConnectionException: HikariPool-x - Connection is not available, request timed out after xms",
                referenceLinks = listOf("https://github.com/airbytehq/airbyte/issues/41614"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "MySQL Timezone Error",
                regexMatchingPattern = ".*is unrecognized or represents more than one time zone*",
                failureType = FailureType.CONFIG,
                externalMessage =
                    "Please configure your database with the correct timezone found in the detailed error message. " +
                        "Please refer to the following documentation: https://dev.mysql.com/doc/refman/8.4/en/time-zone-support.html",
                sampleInternalMessage =
                    "java.lang.RuntimeException: Connector configuration is not valid. Unable to connect: " +
                        "The server time zone value 'PDT' is unrecognized or represents more than one time zone. " +
                        "You must configure either the server or JDBC driver (via the 'connectionTimeZone' configuration property) to " +
                        "use a more specific time zone value if you want to utilize time zone support.",
                referenceLinks =
                    listOf(
                        "https://github.com/airbytehq/airbyte/issues/41614",
                        "https://github.com/airbytehq/oncall/issues/5250",
                    ),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "MySQL Schema change error",
                regexMatchingPattern = ".*whose schema isn't known to this connector*",
                failureType = FailureType.CONFIG,
                externalMessage =
                    "Your connection could not be completed because changes were detected on an unknown table (see detailed error for the table name), " +
                        "please refresh your schema or reset the connection.",
                sampleInternalMessage =
                    "java.lang.RuntimeException: java.lang.RuntimeException: org.apache.kafka.connect.errors." +
                        "ConnectException: An exception occurred in the change event producer. This connector will be stopped.",
                referenceLinks =
                    listOf("https://github.com/airbytehq/airbyte-internal-issues/issues/7156"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "MySQL limit reached",
                regexMatchingPattern =
                    ".*query execution was interrupted, maximum statement execution time exceeded*",
                failureType = FailureType.TRANSIENT,
                externalMessage =
                    "The query took too long to return results, the database read was aborted. Will retry.",
                sampleInternalMessage =
                    "java.lang.RuntimeException: java.lang.RuntimeException: java.sql.SQLException: " +
                        "Query execution was interrupted, maximum statement execution time exceeded",
                referenceLinks =
                    listOf("https://github.com/airbytehq/airbyte-internal-issues/issues/7155"),
            ),
        )
    }
}
