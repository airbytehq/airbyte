/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.integrations.util.ConnectorErrorProfile
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler
import io.airbyte.cdk.integrations.util.FailureType

class PostgresSourceExceptionHandler : ConnectorExceptionHandler() {
    override fun initializeErrorDictionary() {
        val POSTGRES_RECOVERY_CONNECTION_ERROR_MESSAGE =
            "We're having issues syncing from a Postgres replica that is configured as a hot standby server. " +
                "Please see https://go.airbyte.com/pg-hot-standby-error-message for options and workarounds"

        val DATABASE_READ_ERROR = "Encountered an error while reading the database, will retry."

        // include common error profiles
        super.initializeErrorDictionary()

        // adding connector specific error profiles
        add(
            ConnectorErrorProfile(
                errorClass = "Postgres SQL Exception",
                regexMatchingPattern = "(?i).*temporary file size exceeds temp_file_limit.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = DATABASE_READ_ERROR,
                sampleInternalMessage =
                    "org.postgresql.util.PSQLException: ERROR: temporary file size exceeds temp_file_limit",
                referenceLinks =
                    listOf(
                        "https://github.com/airbytehq/airbyte/issues/27090",
                        "https://github.com/airbytehq/oncall/issues/1822",
                    ),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres SQL Exception",
                regexMatchingPattern = "(?i).*an i/o error occured while sending to the backend.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = DATABASE_READ_ERROR,
                sampleInternalMessage =
                    "org.postgresql.util.PSQLException: An I/O error occured while sending to the backend.",
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres Query Conflicts",
                regexMatchingPattern = "(?i).*due to conflict with recovery.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = POSTGRES_RECOVERY_CONNECTION_ERROR_MESSAGE,
                sampleInternalMessage =
                    "ERROR: canceling statement due to conflict with recovery.\n" +
                        "org.postgresql.util.PSQLException: FATAL: terminating connection due to conflict with recovery",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/6296"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres SQL Exception",
                regexMatchingPattern = "(?i).*permission denied for table.*",
                failureType = FailureType.CONFIG,
                externalMessage =
                    "Database read failed due to missing read permissions on a table. See the detailed error for the table name and update permissions accordingly.",
                sampleInternalMessage =
                    "java.lang.RuntimeException: org.postgresql.util.PSQLException: ERROR: permission denied for table xxx.",
                referenceLinks = listOf("https://github.com/airbytehq/airbyte/issues/41614"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres SQL Exception",
                regexMatchingPattern = "(?i).*canceling statement due to statement timeout.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = "Database read failed due SQL statement timeout, will retry.",
                sampleInternalMessage =
                    "org.postgresql.util.PSQLException: ERROR: canceling statement due to statement timeout",
                referenceLinks = listOf("https://github.com/airbytehq/airbyte/issues/41614"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres Hikari Connection Error",
                regexMatchingPattern =
                    "(?i).*connection is not available, request timed out after*",
                failureType = FailureType.TRANSIENT,
                externalMessage = "Database read failed due to connection timeout, will retry.",
                sampleInternalMessage =
                    "java.sql.SQLTransientConnectionException: HikariPool-x - Connection is not available, request timed out after xms",
                referenceLinks =
                    listOf(
                        "https://github.com/airbytehq/airbyte/issues/41614",
                        "https://github.com/airbytehq/oncall/issues/5346",
                    ),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres connection timeout",
                regexMatchingPattern = "(?i).*timed out after [1-9]\\d* msec*",
                failureType = FailureType.TRANSIENT,
                externalMessage = "Database connection timeout, will retry.",
                sampleInternalMessage =
                    "java.util.concurrent.TimeoutException: Timed out after 15000 msec",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/5381"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres Debezium Connection Error",
                regexMatchingPattern = "(?i).*SocketException.*(broken pipe|socket is closed).*",
                failureType = FailureType.TRANSIENT,
                externalMessage =
                    "Database connection error when performing CDC reads, will retry.",
                sampleInternalMessage =
                    "java.net.SocketException: Broken pipe\n" +
                        "java.net.SocketException: Socket is closed",
                referenceLinks =
                    listOf(
                        "https://github.com/airbytehq/oncall/issues/5321",
                        "https://github.com/airbytehq/oncall/issues/5293",
                        "https://github.com/airbytehq/oncall/issues/5750",
                    ),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres Debezium Connection Error",
                regexMatchingPattern = ".*cannot read from logical replication slot.*",
                failureType = FailureType.CONFIG,
                externalMessage =
                    "The configured replication slot has been dropped or has corrupted. Please recreate the replication slot.",
                sampleInternalMessage =
                    "org.postgresql.util.PSQLException: ERROR: cannot read from logical replication slot \"airbyte_slot\"",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/5981"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres SQL Exception",
                regexMatchingPattern = "(?i).*This connection has been closed.*",
                failureType = FailureType.TRANSIENT,
                externalMessage =
                    "The connection to the Postgres server was unexpectedly closed, will retry.",
                sampleInternalMessage =
                    "org.postgresql.util.PSQLException: This connection has been closed.",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/7016"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres Debezium Connection Error",
                regexMatchingPattern = "(?i).*Connection or outbound has closed.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = "The connection to the Postgres server was lost, will retry.",
                sampleInternalMessage =
                    "java.net.SocketException: Connection or outbound has closed",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/5871"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres SQL Exception",
                regexMatchingPattern = "(?i).*recovery is in progress.*",
                failureType = FailureType.TRANSIENT,
                externalMessage = "Postgres server is currently in recovery mode, will retry.",
                sampleInternalMessage =
                    "org.postgresql.util.PSQLException: ERROR: recovery is in progress",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/6033"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres SQL Exception",
                regexMatchingPattern =
                    "(?i).*terminating connection due to idle-in-transaction timeout.*",
                failureType = FailureType.CONFIG,
                externalMessage =
                    "Postgres server closed the connection due to an idle-in-transaction timeout. Please review your server's timeout configuration " +
                        "and increase the timeout if needed",
                sampleInternalMessage =
                    "org.postgresql.util.PSQLException: FATAL: terminating connection due to idle-in-transaction timeout",
                referenceLinks = listOf("https://github.com/airbytehq/oncall/issues/5893"),
            ),
        )

        add(
            ConnectorErrorProfile(
                errorClass = "Postgres Debezium Connection Error",
                regexMatchingPattern =
                    "(?i).*An exception occurred in the change event producer. This connector will be stopped.*",
                failureType = FailureType.TRANSIENT,
                externalMessage =
                    "The sync encountered an unexpected error in the change event producer and has stopped. Please check the logs for details and troubleshoot accordingly.",
                sampleInternalMessage =
                    "io.airbyte.cdk.integrations.source.relationaldb.state.FailedRecordIteratorException: java.lang.RuntimeException: " +
                        "java.lang.RuntimeException: org.apache.kafka.connect.errors.ConnectException: " +
                        "An exception occurred in the change event producer. This connector will be stopped.",
                referenceLinks = listOf("https://github.com/airbytehq/airbyte/issues/41614"),
            ),
        )
    }
}
