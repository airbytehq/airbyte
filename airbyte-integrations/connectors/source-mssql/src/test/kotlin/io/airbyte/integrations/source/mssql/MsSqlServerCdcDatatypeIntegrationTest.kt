/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.read.DatatypeTestCase
import io.airbyte.cdk.read.DatatypeTestOperations
import io.airbyte.cdk.read.DynamicDatatypeTestFactory
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mssql.*
import io.airbyte.integrations.source.mssql.MsSqlServerDatatypeIntegrationTest.Companion.dbContainer
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerCdcReplicationConfigurationSpecification
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerCursorBasedReplicationConfigurationSpecification
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.DynamicContainer
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout

private val log = KotlinLogging.logger {}

class MsSqlServerDatatypeIntegrationTest {

    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> =
        DynamicDatatypeTestFactory(MsSqlServerSourceDatatypeTestOperations).build(dbContainer)

    companion object {

        lateinit var dbContainer: MsSqlServerContainer

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer = MsSqlServerContainerFactory.exclusive(
                MsSqlServerImage.SQLSERVER_2022,
                MsSqlServerContainerFactory.WithNetwork,
            )
        }
    }
}

object MsSqlServerSourceDatatypeTestOperations :
    DatatypeTestOperations<
            MsSqlServerContainer,
            MsSqlServerSourceConfigurationSpecification,
            MsSqlServerSourceConfiguration,
            MsSqlServerSourceConfigurationFactory,
            MsSqlServerSourceDatatypeTestOperations.MsSqlServerSourceDatatypeTestCase
            > {

    private val log = KotlinLogging.logger {}

    override val withGlobal: Boolean = true
    override val globalCursorMetaField: MetaField = MsSqlServerStreamFactory.MsSqlServerCdcMetaFields.CDC_CURSOR

    override fun streamConfigSpec(
        container: MsSqlServerContainer
    ): MsSqlServerSourceConfigurationSpecification =
        container.config.also { it.setReplicationMethodValue(MsSqlServerCursorBasedReplicationConfigurationSpecification()) }

    override fun globalConfigSpec(
        container: MsSqlServerContainer
    ): MsSqlServerSourceConfigurationSpecification =
        container.config.also { it.setReplicationMethodValue(MsSqlServerCursorBasedReplicationConfigurationSpecification()) }

    // container.config.also { it.setReplicationMethodValue(MsSqlServerCdcReplicationConfigurationSpecification()) }

    override val configFactory: MsSqlServerSourceConfigurationFactory = MsSqlServerSourceConfigurationFactory()

    override fun createStreams(config: MsSqlServerSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false
            for ((_, case) in testCases) {
                for (ddl in case.ddl) {
                    log.info { "test case ${case.id}: executing $ddl" }
                    connection.createStatement().use { stmt -> stmt.execute(ddl) }
                }
            }
        }
    }

    override fun populateStreams(config: MsSqlServerSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false
            for ((_, case) in testCases) {
                for (dml in case.dml) {
                    log.info { "test case ${case.id}: executing $dml" }
                    connection.createStatement().use { stmt -> stmt.execute(dml) }
                }
            }
        }
    }

    val bitValues =
        mapOf(
            "1" to "true",
            "0" to "false",
        )

    val longBitValues =
        mapOf(
            "b'10101010'" to """"qg=="""",
        )

    val stringValues =
        mapOf(
            "'abcdef'" to """"abcdef"""",
            "'ABCD'" to """"ABCD"""",
            "'OXBEEF'" to """"OXBEEF"""",
        )

    val yearValues =
        mapOf(
            "1992" to """1992""",
            "2002" to """2002""",
            "70" to """1970""",
        )

    val precisionTwoDecimalValues =
        mapOf(
            "0.2" to """0.2""",
        )

    val floatValues =
        mapOf(
            "123.4567" to """123.4567""",
        )

    val zeroPrecisionDecimalValues =
        mapOf(
            "2" to """2.0""",
        )

    val tinyintValues =
        mapOf(
            "10" to "10",
            "4" to "4",
            "2" to "2",
        )

    val intValues =
        mapOf(
            "10" to "10",
            "100000000" to "100000000",
            "200000000" to "200000000",
        )

    val dateValues =
        mapOf(
            "'2022-01-01'" to """"2022-01-01"""",
        )

    val timeValues =
        mapOf(
            "'14:30:00'" to """"14:30:00.000000"""",
        )

    val dateTimeValues =
        mapOf(
            "'2024-09-13 14:30:00'" to """"2024-09-13T14:30:00.000000"""",
            "'2024-09-13T14:40:00'" to """"2024-09-13T14:40:00.000000"""",
        )

    val timestampValues =
        mapOf(
            "'2024-09-12 14:30:00'" to """"2024-09-12T14:30:00.000000Z"""",
            "CONVERT_TZ('2024-09-12 14:30:00', 'America/Los_Angeles', 'UTC')" to
                    """"2024-09-12T21:30:00.000000Z"""",
        )

    val booleanValues =
        mapOf(
            "TRUE" to "true",
            "FALSE" to "false",
        )

    override val testCases: Map<String, MsSqlServerSourceDatatypeTestCase> =
        listOf(
            MsSqlServerSourceDatatypeTestCase(
                "VARCHAR(10)",
                stringValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.STRING,
            ),
            MsSqlServerSourceDatatypeTestCase(
                "DECIMAL(10,2)",
                precisionTwoDecimalValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
            ),
            MsSqlServerSourceDatatypeTestCase(
                "FLOAT",
                precisionTwoDecimalValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.NUMBER
            ),
            MsSqlServerSourceDatatypeTestCase(
                "FLOAT(7)",
                floatValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
            ),
            MsSqlServerSourceDatatypeTestCase(
                "FLOAT(53)",
                floatValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.NUMBER,
            ),
            MsSqlServerSourceDatatypeTestCase(
                "TINYINT",
                tinyintValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.INTEGER,
            ),
            MsSqlServerSourceDatatypeTestCase(
                "SMALLINT",
                tinyintValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.INTEGER,
            ),
            MsSqlServerSourceDatatypeTestCase("BIGINT", intValues, expectedAirbyteSchemaType = LeafAirbyteSchemaType.INTEGER),
            MsSqlServerSourceDatatypeTestCase("INT", intValues, expectedAirbyteSchemaType = LeafAirbyteSchemaType.INTEGER),
            MsSqlServerSourceDatatypeTestCase("DATE", dateValues, expectedAirbyteSchemaType = LeafAirbyteSchemaType.DATE),
            /*TestCase(
                    "TIMESTAMP",
                    timestampValues,
                    airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                ),*/
            MsSqlServerSourceDatatypeTestCase(
                "DATETIME",
                dateTimeValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            ),
            MsSqlServerSourceDatatypeTestCase(
                "TIME",
                timeValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
            ),
            MsSqlServerSourceDatatypeTestCase(
                "BIT",
                bitValues,
                expectedAirbyteSchemaType = LeafAirbyteSchemaType.BOOLEAN,
            ),
        )
            .associateBy { it.id }

    data class MsSqlServerSourceDatatypeTestCase(
        val sqlType: String,
        val sqlToAirbyte: Map<String, String>,
        override val expectedAirbyteSchemaType: AirbyteSchemaType,
        override val isGlobal: Boolean = true,
    ) : DatatypeTestCase {

        override val isStream: Boolean
            get() = true

        private val typeName: String
            get() =
                sqlType
                    .replace("[^a-zA-Z0-9]".toRegex(), " ")
                    .trim()
                    .replace(" +".toRegex(), "_")
                    .lowercase()

        override val id: String
            get() = "tbl_$typeName"

        override val fieldName: String
            get() = "col_$typeName"

        override val expectedData: List<String>
            get() = sqlToAirbyte.values.map { """{"${fieldName}":$it}""" }

        val ddl: List<String>
            get() =
                listOf(
                    "CREATE TABLE ${dbContainer.databaseName}.${dbContainer.schemaName}.$id " + "($fieldName $sqlType PRIMARY KEY)"

                )

        val dml: List<String>
            get() =
                sqlToAirbyte.keys.map {
                    if (it == "NULL") {
                        "INSERT INTO ${dbContainer.databaseName}.${dbContainer.schemaName}.$id VALUES ()"
                    } else {
                        "INSERT INTO ${dbContainer.databaseName}.${dbContainer.schemaName}.$id ($fieldName) VALUES ($it)"
                    }
                }
    }
}
