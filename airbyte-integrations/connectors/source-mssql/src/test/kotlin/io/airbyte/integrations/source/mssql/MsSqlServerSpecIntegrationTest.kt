/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import java.nio.file.Files
import java.nio.file.Paths
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MsSqlServerSpecIntegrationTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected_spec.json")
    }

    @Test
    fun testCheck() {
        val it = MsSqlServerContainerFactory.shared(MsSqlServerImage.SQLSERVER_2022)
        SyncsTestFixture.testCheck(it.config)
    }

    @Test
    fun testDiscover() {
        val container = MsSqlServerContainerFactory.shared(MsSqlServerImage.SQLSERVER_2022)
        val config = container.config
        val discoverOutput: BufferingOutputConsumer = CliRunner.source("discover", config).run()
        Assertions.assertEquals(
            listOf(
                AirbyteCatalog()
                    .withStreams(
                        listOf(
                            AirbyteStream()
                                .withName("id_name_and_born")
                                .withJsonSchema(
                                    Jsons.readTree(
                                        """{"type":"object","properties":{"born":{"type":"string"},"name":{"type":"string"},"id":{"type":"number","airbyte_type":"integer"}}}"""
                                    )
                                )
                                .withSupportedSyncModes(
                                    listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                                )
                                .withSourceDefinedCursor(false)
                                .withNamespace(config.schemas!![0])
                                .withSourceDefinedPrimaryKey(listOf(listOf("id")))
                                .withIsResumable(true),
                            AirbyteStream()
                                .withName("name_and_born")
                                .withJsonSchema(
                                    Jsons.readTree(
                                        """{"type":"object","properties":{"born":{"type":"string"},"name":{"type":"string"}}}"""
                                    )
                                )
                                .withSupportedSyncModes(
                                    listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                                )
                                .withSourceDefinedCursor(false)
                                .withNamespace(config.schemas!![0])
                        )
                    )
            ),
            discoverOutput.catalogs()
        )
    }

    @Test
    fun testSync() {
        val container = MsSqlServerContainerFactory.shared(MsSqlServerImage.SQLSERVER_2022)
        val config = container.config
        val configuredCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        "name_and_born",
                                        config.schemas!![0],
                                        Field.of("name", JsonSchemaType.STRING),
                                        Field.of("born", JsonSchemaType.STRING)
                                    )
                                    .withSupportedSyncModes(
                                        listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                                    )
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("id"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        "id_name_and_born",
                                        config.schemas!![0],
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                        Field.of("born", JsonSchemaType.STRING)
                                    )
                                    .withSupportedSyncModes(
                                        listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                                    )
                            )
                    )
                )

        val readOutput: BufferingOutputConsumer =
            CliRunner.source("read", config, configuredCatalog, listOf()).run()
        // println("SGXX
        // records=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.records())}")
        println(
            "SGXX: specs=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.specs())}"
        )
        println(
            "SGXX logs=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.logs())}"
        )
        println(
            "SGXX states=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.states())}"
        )
        println(
            "SGXX statuses=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.statuses())}"
        )
        // println("SGXX
        // messages=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.messages())}")
        println(
            "SGXX traces=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.traces())}"
        )
        // println("SGXX
        // readOutput=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput)}")

    }

    @Test
    fun testSync2() {
        val container =
        MsSqlServerContainerFactory.shared(MsSqlServerImage.SQLSERVER_2022)
        val config =
            container.config

        val catalog =
            SyncsTestFixture.configuredCatalogFromResource("catalog-cdc-single-stream.json")
        CliRunner.source("discover", config).run()
        println(
            "SGX catalogString=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(catalog)}"
        )

        val readOutput: BufferingOutputConsumer =
            CliRunner.source("read", config, catalog, listOf()).run()
        // println("SGXX
        // records=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.records())}")
        println(
            "SGXX: specs=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.specs())}"
        )
        println(
            "SGXX logs=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.logs())}"
        )
        println(
            "SGXX states=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.states())}"
        )
        println(
            "SGXX statuses=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.statuses())}"
        )
        // println("SGXX
        // messages=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.messages())}")
        println(
            "SGXX traces=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.traces())}"
        )
        // println("SGXX
        // readOutput=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput)}")

    }

    @Test
    fun testSyncWithAlwaysNullCursor() {
        val container =
            MsSqlServerContainerFactory.shared(MsSqlServerImage.SQLSERVER_2022)
        val config =
            container.config

        val catalog = SyncsTestFixture.configuredCatalogFromResource("catalog-cdc-dbo-users.json")
        CliRunner.source("discover", config).run()
        println(
            "SGX catalogString=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(catalog)}"
        )

        val readOutput: BufferingOutputConsumer =
            CliRunner.source("read", config, catalog, listOf()).run()
        // println("SGXX
        // records=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.records())}")
        println(
            "SGXX: specs=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.specs())}"
        )
        println(
            "SGXX logs=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.logs())}"
        )
        println(
            "SGXX states=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.states())}"
        )
        println(
            "SGXX statuses=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.statuses())}"
        )
        // println("SGXX
        // messages=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.messages())}")
        println(
            "SGXX traces=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.traces())}"
        )
        // println("SGXX
        // readOutput=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput)}")

    }

    @Test
    fun testSyncEmptyTable() {
        val container =
            MsSqlServerContainerFactory.shared(MsSqlServerImage.SQLSERVER_2022)
        val config =
            container.config
        val configuredCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withCursorField(listOf("born"))
                            .withPrimaryKey(listOf(listOf("born")))
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        "name_born",
                                        "dbo",
                                        Field.of("name", JsonSchemaType.STRING),
                                        Field.of("born", JsonSchemaType.STRING)
                                    )
                                    .withSupportedSyncModes(listOf(SyncMode.INCREMENTAL))
                            )
                    )
                )
        CliRunner.source("discover", config).run()
        println(
            "SGX catalogString=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(configuredCatalog)}"
        )

        val readOutput: BufferingOutputConsumer =
            CliRunner.source("read", config, configuredCatalog, listOf()).run()
        println(
            "SGXX messages=${ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(readOutput.messages())}"
        )
    }
}
