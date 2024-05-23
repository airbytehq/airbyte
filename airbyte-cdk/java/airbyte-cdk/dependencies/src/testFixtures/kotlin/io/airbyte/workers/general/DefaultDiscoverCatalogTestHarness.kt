/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.general

import io.airbyte.api.client.AirbyteApiClient
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaWriteRequestBody
import io.airbyte.commons.io.LineGobbler
import io.airbyte.commons.json.Jsons
import io.airbyte.configoss.ConnectorJobOutput
import io.airbyte.configoss.StandardDiscoverCatalogInput
import io.airbyte.protocol.models.AirbyteCatalog
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.workers.TestHarnessUtils
import io.airbyte.workers.WorkerConstants
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.helper.CatalogClientConverters
import io.airbyte.workers.helper.ConnectorConfigUpdater
import io.airbyte.workers.internal.AirbyteStreamFactory
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory
import io.airbyte.workers.process.IntegrationLauncher
import java.nio.file.Path
import java.util.*
import kotlin.concurrent.Volatile
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class DefaultDiscoverCatalogTestHarness
@JvmOverloads
constructor(
    private val airbyteApiClient: AirbyteApiClient,
    private val integrationLauncher: IntegrationLauncher,
    private val connectorConfigUpdater: ConnectorConfigUpdater,
    private val streamFactory: AirbyteStreamFactory = DefaultAirbyteStreamFactory()
) : DiscoverCatalogTestHarness {
    @Volatile private lateinit var process: Process

    @Throws(TestHarnessException::class)
    override fun run(
        discoverSchemaInput: StandardDiscoverCatalogInput,
        jobRoot: Path
    ): ConnectorJobOutput {
        try {
            val inputConfig = discoverSchemaInput.connectionConfiguration
            process =
                integrationLauncher.discover(
                    jobRoot,
                    WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
                    Jsons.serialize(inputConfig)
                )

            val jobOutput =
                ConnectorJobOutput()
                    .withOutputType(ConnectorJobOutput.OutputType.DISCOVER_CATALOG_ID)

            LineGobbler.gobble(process.errorStream, { msg: String -> LOGGER.error(msg) })

            val messagesByType = TestHarnessUtils.getMessagesByType(process, streamFactory, 30)

            val catalog =
                messagesByType
                    .getOrDefault(AirbyteMessage.Type.CATALOG, ArrayList())
                    .map { obj: AirbyteMessage -> obj.catalog }
                    .firstOrNull()

            val optionalConfigMsg =
                TestHarnessUtils.getMostRecentConfigControlMessage(messagesByType)
            if (
                optionalConfigMsg.isPresent &&
                    TestHarnessUtils.getDidControlMessageChangeConfig(
                        inputConfig,
                        optionalConfigMsg.get()
                    )
            ) {
                connectorConfigUpdater.updateSource(
                    UUID.fromString(discoverSchemaInput.sourceId),
                    optionalConfigMsg.get().config
                )
                jobOutput.connectorConfigurationUpdated = true
            }

            val failureReason =
                TestHarnessUtils.getJobFailureReasonFromMessages(
                    ConnectorJobOutput.OutputType.DISCOVER_CATALOG_ID,
                    messagesByType
                )
            failureReason.ifPresent { jobOutput.failureReason = it }

            val exitCode = process.exitValue()
            if (exitCode != 0) {
                LOGGER.warn("Discover job subprocess finished with exit codee {}", exitCode)
            }

            if (catalog != null) {
                val result =
                    AirbyteApiClient.retryWithJitter(
                        {
                            airbyteApiClient.sourceApi.writeDiscoverCatalogResult(
                                buildSourceDiscoverSchemaWriteRequestBody(
                                    discoverSchemaInput,
                                    catalog
                                )
                            )
                        },
                        WRITE_DISCOVER_CATALOG_LOGS_TAG
                    )!!
                jobOutput.discoverCatalogId = result.catalogId
            } else if (failureReason.isEmpty) {
                TestHarnessUtils.throwWorkerException(
                    "Integration failed to output a catalog struct and did not output a failure reason",
                    process
                )
            }
            return jobOutput
        } catch (e: TestHarnessException) {
            throw e
        } catch (e: Exception) {
            throw TestHarnessException("Error while discovering schema", e)
        }
    }

    private fun buildSourceDiscoverSchemaWriteRequestBody(
        discoverSchemaInput: StandardDiscoverCatalogInput,
        catalog: AirbyteCatalog
    ): SourceDiscoverSchemaWriteRequestBody {
        return SourceDiscoverSchemaWriteRequestBody()
            .catalog(CatalogClientConverters.toAirbyteCatalogClientApi(catalog))
            .sourceId( // NOTE: sourceId is marked required in the OpenAPI config but the code
                // generator doesn't enforce
                // it, so we check again here.
                if (discoverSchemaInput.sourceId == null) null
                else UUID.fromString(discoverSchemaInput.sourceId)
            )
            .connectorVersion(discoverSchemaInput.connectorVersion)
            .configurationHash(discoverSchemaInput.configHash)
    }

    override fun cancel() {
        TestHarnessUtils.cancelProcess(process)
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(DefaultDiscoverCatalogTestHarness::class.java)
        private const val WRITE_DISCOVER_CATALOG_LOGS_TAG = "call to write discover schema result"
    }
}
