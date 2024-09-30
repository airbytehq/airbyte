package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.configoss.OperatorDbt
import io.airbyte.protocol.models.v0.*
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.general.DbtTransformationRunner
import io.airbyte.workers.normalization.DefaultNormalizationRunner
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ArgumentsSource
import java.nio.file.Files
import java.util.ArrayList
import java.util.concurrent.TimeUnit

abstract class RecordBasedWithNormalizationAndDbtDestinationAcceptanceTest(

): RecordBasedDestinationAcceptanceTest() {
    protected open fun dbtFromDefinition(): Boolean {
        val metadata = readMetadata()["data"] ?: return false
        val supportsDbt = metadata["supportsDbt"]
        return supportsDbt != null && supportsDbt.asBoolean(false)
    }


    @Test
    fun normalizationFromDefinitionValueShouldBeCorrect() {
        if (normalizationFromDefinition()) {
            var normalizationRunnerFactorySupportsDestinationImage: Boolean
            try {
                DefaultNormalizationRunner(
                    processFactory,
                    getNormalizationImageName(),
                    getNormalizationIntegrationType()
                )
                normalizationRunnerFactorySupportsDestinationImage = true
            } catch (e: IllegalStateException) {
                normalizationRunnerFactorySupportsDestinationImage = false
            }
            Assertions.assertEquals(
                normalizationFromDefinition(),
                normalizationRunnerFactorySupportsDestinationImage
            )
        }
    }

    @Test
    @Throws(Exception::class)
    fun testCustomDbtTransformationsFailure() {
        if (!normalizationFromDefinition() || !dbtFromDefinition()) {
            // we require normalization implementation for this destination, because we make sure to
            // install
            // required dbt dependency in the normalization docker image in order to run this test
            // successfully
            // (we don't actually rely on normalization running anything here though)
            return
        }

        val config = getConfig()

        val runner =
            DbtTransformationRunner(
                processFactory,
                DefaultNormalizationRunner(
                    processFactory,
                    getNormalizationImageName(),
                    getNormalizationIntegrationType()
                )
            )
        runner.start()
        val transformationRoot = Files.createDirectories(jobRoot.resolve("transform"))
        val dbtConfig =
            OperatorDbt()
                .withGitRepoUrl("https://github.com/fishtown-analytics/dbt-learn-demo.git")
                .withGitRepoBranch("main")
                .withDockerImage("fishtownanalytics/dbt:0.19.1")
                .withDbtArguments("debug")
        if (!runner.run(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt debug Failed.")
        }

        dbtConfig.withDbtArguments("test")
        Assertions.assertFalse(
            runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig),
            "dbt test should fail, as we haven't run dbt run on this project yet"
        )
    }

    @ArgumentsSource(DataArgumentsProvider::class)
    @Test
    @Throws(Exception::class)
    fun testIncrementalSyncWithNormalizationDropOneColumn() {
        if (!normalizationFromDefinition() || !supportIncrementalSchemaChanges()) {
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        ProtocolVersion.V0
                    )
                ),
                AirbyteCatalog::class.java
            )

        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach { s ->
            s.withSyncMode(SyncMode.INCREMENTAL)
            s.withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            s.withCursorField(emptyList())
            // use composite primary key of various types (string, float)
            s.withPrimaryKey(
                java.util.List.of(
                    listOf("id"),
                    listOf("currency"),
                    listOf("date"),
                    listOf("NZD"),
                    listOf("USD")
                )
            )
        }

        var messages =
            MoreResources.readResource(
                DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    ProtocolVersion.V0
                )
            )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
                .toMutableList()

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        val defaultSchema = getDefaultSchema(config)
        var actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)
        assertSameMessages(messages, actualMessages, true)

        // remove one field
        val jsonSchema = configuredCatalog.streams[0].stream.jsonSchema
        (jsonSchema.findValue("properties") as ObjectNode).remove("HKD")
        // insert more messages
        // NOTE: we re-read the messages because `assertSameMessages` above pruned the emittedAt
        // timestamps.
        messages =
            MoreResources.readResource(
                DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    ProtocolVersion.V0
                )
            )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
                .toMutableList()
        messages.addLast(
            Jsons.deserialize(
                "{\"type\": \"RECORD\", \"record\": {\"stream\": \"exchange_rate\", \"emitted_at\": 1602637989500, \"data\": { \"id\": 2, \"currency\": \"EUR\", \"date\": \"2020-09-02T00:00:00Z\", \"NZD\": 1.14, \"USD\": 10.16}}}\n",
                AirbyteMessage::class.java
            )
        )

        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        // assert the removed field is missing on the new messages
        actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)

        // We expect all the of messages to be missing the removed column after normalization.
        val expectedMessages =
            messages.map { message: AirbyteMessage ->
                if (message.record != null) {
                    (message.record.data as ObjectNode).remove("HKD")
                }
                message
            }

        assertSameMessages(expectedMessages, actualMessages, true)
    }

    /**
     * Verify that the integration successfully writes records successfully both raw and normalized.
     * Tests a wide variety of messages an schemas (aspirationally, anyway).
     */
    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    // Normalization is a pretty slow process. Increase our test timeout.
    @Timeout(value = 300, unit = TimeUnit.SECONDS)
    open fun testSyncWithNormalization(messagesFilename: String, catalogFilename: String) {
        if (!normalizationFromDefinition()) {
            return
        }

        val catalog =
            Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            MoreResources.readResource(messagesFilename).trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        val defaultSchema = getDefaultSchema(config)
        val actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)
        assertSameMessages(messages, actualMessages, true)
    }


    @Test
    @Throws(Exception::class)
    open fun testCustomDbtTransformations() {
        if (!dbtFromDefinition()) {
            return
        }

        val config = getConfig()

        // This may throw IllegalStateException "Requesting normalization, but it is not included in
        // the
        // normalization mappings"
        // We indeed require normalization implementation of the 'transform_config' function for
        // this
        // destination,
        // because we make sure to install required dbt dependency in the normalization docker image
        // in
        // order to run
        // this test successfully and that we are able to convert a destination 'config.json' into a
        // dbt
        // 'profiles.yml'
        // (we don't actually rely on normalization running anything else here though)
        val runner =
            DbtTransformationRunner(
                processFactory,
                DefaultNormalizationRunner(
                    processFactory,
                    getNormalizationImageName(),
                    getNormalizationIntegrationType()
                )
            )
        runner.start()
        val transformationRoot = Files.createDirectories(jobRoot.resolve("transform"))
        val dbtConfig =
            OperatorDbt() // Forked from https://github.com/dbt-labs/jaffle_shop because they made a
                // change that would have
                // required a dbt version upgrade
                // https://github.com/dbt-labs/jaffle_shop/commit/b1680f3278437c081c735b7ea71c2ff9707bc75f#diff-27386df54b2629c1191d8342d3725ed8678413cfa13b5556f59d69d33fae5425R20
                // We're actually two commits upstream of that, because the previous commit
                // (https://github.com/dbt-labs/jaffle_shop/commit/ec36ae177ab5cb79da39ff8ab068c878fbac13a0) also
                // breaks something
                // TODO once we're on DBT 1.x, switch this back to using the main branch
                .withGitRepoUrl("https://github.com/airbytehq/jaffle_shop.git")
                .withGitRepoBranch("pre_dbt_upgrade")
                .withDockerImage(getNormalizationImageName())
        //
        // jaffle_shop is a fictional ecommerce store maintained by fishtownanalytics/dbt.
        //
        // This dbt project transforms raw data from an app database into a customers and orders
        // model ready
        // for analytics.
        // The repo is a self-contained playground dbt project, useful for testing out scripts, and
        // communicating some of the core dbt concepts:
        //
        // 1. First, it tests if connection to the destination works.
        dbtConfig.withDbtArguments("debug")
        if (!runner.run(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt debug Failed.")
        }
        // 2. Install any dependencies packages, if any
        dbtConfig.withDbtArguments("deps")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt deps Failed.")
        }
        // 3. It contains seeds that includes some (fake) raw data from a fictional app as CSVs data
        // sets.
        // This materializes the CSVs as tables in your target schema.
        // Note that a typical dbt project does not require this step since dbt assumes your raw
        // data is
        // already in your warehouse.
        dbtConfig.withDbtArguments("seed")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt seed Failed.")
        }
        // 4. Run the models:
        // Note: If this steps fails, it might mean that you need to make small changes to the SQL
        // in the
        // models folder to adjust for the flavor of SQL of your target database.
        dbtConfig.withDbtArguments("run")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt run Failed.")
        }
        // 5. Test the output of the models and tables have been properly populated:
        dbtConfig.withDbtArguments("test")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt test Failed.")
        }
        // 6. Generate dbt documentation for the project:
        // This step is commented out because it takes a long time, but is not vital for Airbyte
        // dbtConfig.withDbtArguments("docs generate");
        // if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig))
        // {
        // throw new WorkerException("dbt docs generate Failed.");
        // }
        runner.close()
    }
}
