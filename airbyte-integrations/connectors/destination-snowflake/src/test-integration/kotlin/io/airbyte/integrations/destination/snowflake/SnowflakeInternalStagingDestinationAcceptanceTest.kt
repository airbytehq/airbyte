/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.configoss.StandardCheckConnectionOutput
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import java.nio.file.Path
import org.assertj.core.api.AssertionsForClassTypes
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ArgumentsSource

@Disabled
class SnowflakeInternalStagingDestinationAcceptanceTest :
    SnowflakeInsertDestinationAcceptanceTest() {
    override val staticConfig: JsonNode
        get() = deserialize(readFile(Path.of("secrets/internal_staging_config.json")))

    @Disabled("See README for why this test is disabled")
    @Test
    @Throws(Exception::class)
    fun testCheckWithNoProperStagingPermissionConnection() {
        // Config to user (creds) that has no permission to write
        val config =
            deserialize(readFile(Path.of("secrets/copy_insufficient_staging_roles_config.json")))

        val standardCheckConnectionOutput = runCheck(config)

        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.FAILED,
            standardCheckConnectionOutput.status
        )
        AssertionsForClassTypes.assertThat(standardCheckConnectionOutput.message)
            .contains(NO_USER_PRIVILEGES_ERR_MSG)
    }

    @Disabled("See README for why this test is disabled")
    @Test
    @Throws(Exception::class)
    fun testCheckWithNoActiveWarehouseConnection() {
        // Config to user(creds) that has no warehouse assigned
        val config =
            deserialize(
                readFile(Path.of("secrets/internal_staging_config_no_active_warehouse.json"))
            )

        val standardCheckConnectionOutput = runCheck(config)

        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.FAILED,
            standardCheckConnectionOutput.status
        )
        AssertionsForClassTypes.assertThat(standardCheckConnectionOutput.message)
            .contains(
                SnowflakeInsertDestinationAcceptanceTest.Companion.NO_ACTIVE_WAREHOUSE_ERR_MSG
            )
    }

    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    fun testSyncWithNormalizationWithKeyPairAuth(
        messagesFilename: String,
        catalogFilename: String
    ) {
        testSyncWithNormalizationWithKeyPairAuth(
            messagesFilename,
            catalogFilename,
            "secrets/config_key_pair.json"
        )
    }

    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    fun testSyncWithNormalizationWithKeyPairEncrypt(
        messagesFilename: String,
        catalogFilename: String
    ) {
        testSyncWithNormalizationWithKeyPairAuth(
            messagesFilename,
            catalogFilename,
            "secrets/config_key_pair_encrypted.json"
        )
    }

    @Throws(Exception::class)
    private fun testSyncWithNormalizationWithKeyPairAuth(
        messagesFilename: String,
        catalogFilename: String,
        configName: String
    ) {
        if (!normalizationFromDefinition()) {
            return
        }

        val catalog = deserialize(readResource(catalogFilename), AirbyteCatalog::class.java)
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages: List<AirbyteMessage> =
            readResource(messagesFilename)
                .lines()
                .map { record: String? -> deserialize(record, AirbyteMessage::class.java) }
                .toList()

        val config = deserialize(readFile(Path.of(configName)))
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        val defaultSchema = getDefaultSchema(config)
        val actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)
        assertSameMessages(messages, actualMessages, true)
    }
}
