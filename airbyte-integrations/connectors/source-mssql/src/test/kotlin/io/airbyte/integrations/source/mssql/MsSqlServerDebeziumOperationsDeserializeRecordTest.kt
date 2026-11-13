/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.DefaultExceptionClassifier
import io.airbyte.cdk.output.SystemError
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.every
import io.mockk.mockk
import java.net.InetSocketAddress
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MsSqlServerDebeziumOperationsDeserializeRecordTest {
    private val stream =
        Stream(
            id =
                StreamIdentifier.from(StreamDescriptor().withName("AUSENCIA").withNamespace("dbo")),
            schema =
                setOf(
                    EmittedField(
                        "AU_FECHA",
                        MsSqlSourceOperations.MsSqlServerLocalDateTimeFieldType,
                    ),
                ),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = null,
            configuredCursor = null,
        )

    @Test
    fun numericValueForLocalDateTimeFieldThrowsSafeSystemError() {
        assertInvalidValue(
            """
            {
              "before": null,
              "after": {"AU_FECHA": 1792022400000},
              "source": {"ts_ms": 1792022400000, "change_lsn": "00000001:00000001:0001", "commit_lsn": "00000001:00000001:0001", "event_serial_no": 0}
            }
            """
                .trimIndent(),
        )
    }

    @Test
    fun numericValueForLocalDateTimeFieldThrowsSafeSystemErrorForDelete() {
        assertInvalidValue(
            """
            {
              "before": {"AU_FECHA": 1792022400000},
              "after": null,
              "source": {"ts_ms": 1792022400000, "change_lsn": "00000001:00000001:0001", "commit_lsn": "00000001:00000001:0001", "event_serial_no": 0}
            }
            """
                .trimIndent(),
        )
    }

    @Test
    fun textualLocalDateTimeValueDecodes() {
        val result =
            debeziumOperations()
                .deserializeRecord(
                    DebeziumRecordKey(Jsons.readTree("{}")),
                    DebeziumRecordValue(
                        Jsons.readTree(
                            """
                            {
                              "before": null,
                              "after": {"AU_FECHA": "2026-10-15T00:00:00"},
                              "source": {"ts_ms": 1792022400000, "change_lsn": "00000001:00000001:0001", "commit_lsn": "00000001:00000001:0001", "event_serial_no": 0}
                            }
                            """
                                .trimIndent(),
                        ),
                    ),
                    stream,
                )

        Assertions.assertTrue(result.data.containsKey("AU_FECHA"))
    }

    private fun assertInvalidValue(value: String) {
        val message =
            "CDC change event value for column \"AU_FECHA\" in stream \"AUSENCIA\" does not match the column's discovered type timestamp_without_timezone."
        val exception =
            Assertions.assertThrows(SystemErrorException::class.java) {
                debeziumOperations()
                    .deserializeRecord(
                        DebeziumRecordKey(Jsons.readTree("{}")),
                        DebeziumRecordValue(Jsons.readTree(value)),
                        stream,
                    )
            }

        Assertions.assertEquals(message, exception.message)
        Assertions.assertFalse(exception.message!!.contains("1792022400000"))
        Assertions.assertTrue(exception.cause is IllegalArgumentException)
        Assertions.assertTrue(exception.cause!!.message!!.contains("1792022400000"))
        Assertions.assertEquals(
            SystemError(message),
            DefaultExceptionClassifier(1).classify(exception),
        )
    }

    private fun debeziumOperations(): MsSqlServerDebeziumOperations {
        val configuration = MsSqlServerSourceConfigurationFactory().make(cdcPojo())
        val tunnelSession = mockk<TunnelSession>()
        every { tunnelSession.address } returns InetSocketAddress("localhost", 1433)
        val jdbcConnectionFactory = mockk<JdbcConnectionFactory>()
        every { jdbcConnectionFactory.ensureTunnelSession() } returns tunnelSession

        return MsSqlServerDebeziumOperations(jdbcConnectionFactory, configuration)
    }

    private fun cdcPojo(): MsSqlServerSourceConfigurationSpecification =
        MsSqlServerSourceConfigurationSpecification().also {
            it.host = "localhost"
            it.port = 1433
            it.database = "testdb"
            it.username = "sa"
            it.password = "Password123!"
            it.encryptionJson =
                MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification
            it.replicationMethodJson = Cdc()
        }
}
