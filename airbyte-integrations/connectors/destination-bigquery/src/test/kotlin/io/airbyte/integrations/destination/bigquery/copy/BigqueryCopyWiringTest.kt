/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import com.google.cloud.bigquery.BigQuery
import io.airbyte.cdk.Operation
import io.airbyte.cdk.fusion.FusionConfiguration
import io.airbyte.cdk.load.check.DestinationCheckerSync
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.DestinationSuccess
import io.airbyte.cdk.load.state.FreeingAnnotatingCheckpointConsumer
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.WriteOperation
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.spec.SpecOperation
import io.airbyte.cdk.spec.SpecificationFactory
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfigurationFactory
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.spec.GcsFilePostProcessing
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.ApplicationContext
import io.micronaut.inject.qualifiers.Qualifiers
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.File
import java.net.URLClassLoader
import java.nio.file.Files
import java.nio.file.Path
import java.util.UUID
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

class BigqueryCopyWiringTest {
    @TempDir lateinit var directory: Path

    @Test
    fun `spec and checker internal write ignore invalid archive environment in actual DI`() {
        runProbe("nonwrite", "not-a-boolean")
    }

    @Test
    fun `disabled write does not construct archive with invalid environment`() {
        runProbe("disabled", "false")
    }

    @Test
    fun `enabled write uses environment routing`() {
        runProbe("write", "true")
    }

    /** Isolate the process environment while connector tests run in parallel. */
    private fun runProbe(scenario: String, enabled: String) {
        val classpath =
            (System.getProperty("java.class.path").split(File.pathSeparator) +
                    generateSequence(javaClass.classLoader) { it.parent }
                        .filterIsInstance<URLClassLoader>()
                        .flatMap { it.urLs.asSequence() }
                        .filter { it.protocol == "file" }
                        .map { Path.of(it.toURI()).toString() }
                        .toList())
                .distinct()
                .joinToString(File.pathSeparator)
        val log = directory.resolve("$scenario.log")
        val builder =
            ProcessBuilder(
                    Path.of(System.getProperty("java.home"), "bin", "java").toString(),
                    "-Xmx512m",
                    "-cp",
                    classpath,
                    BigqueryCopyWiringProbe::class.java.name,
                    scenario,
                )
                .redirectErrorStream(true)
                .redirectOutput(log.toFile())
        builder.environment().apply {
            keys
                .filter { it.startsWith("AIRBYTE_FUSION_") || it.startsWith("AWS_") }
                .toList()
                .forEach { remove(it) }
            put("AIRBYTE_FUSION_ENABLED", enabled)
            put("AIRBYTE_FUSION_S3_ROLE_ARN", "invalid-enabled-only-field")
            listOf("ORGANIZATION", "WORKSPACE", "SOURCE", "CONNECTION", "DESTINATION").forEach {
                put(
                    "AIRBYTE_${it}_ID",
                    if (enabled == "true") UUID(0, 42).toString() else "invalid-environment-id"
                )
            }
            if (enabled == "true") {
                put("AIRBYTE_FUSION_S3_BUCKET", "platform-bucket")
                put("AIRBYTE_FUSION_S3_REGION", "us-east-2")
                put("AIRBYTE_FUSION_S3_ROLE_ARN", "arn:aws:iam::123456789012:role/platform")
            }
            put("AWS_EC2_METADATA_DISABLED", "true")
        }
        val process = builder.start()
        try {
            assertTrue(
                process.waitFor(60, TimeUnit.SECONDS),
                "Wiring probe timed out: ${Files.readString(log)}",
            )
            assertEquals(0, process.exitValue(), Files.readString(log))
        } finally {
            if (process.isAlive) process.destroyForcibly().waitFor(10, TimeUnit.SECONDS)
        }
    }
}

/**
 * Runs only in the subprocess above, with real Micronaut factory definitions and CLI properties.
 */
object BigqueryCopyWiringProbe {
    @JvmStatic
    fun main(args: Array<String>) {
        if (args.single() == "nonwrite") {
            specWithoutCustomerConfiguration()
            for (gcs in listOf(false, true)) {
                for (raw in listOf(false, true)) checkInternalWrite(gcs, raw)
            }
        } else {
            for (gcs in listOf(false, true)) {
                for (raw in listOf(false, true)) {
                    context("write").use { context ->
                        registerConnectorInputs(context, gcs, raw)
                        context.start()
                        if (args.single() == "disabled") {
                            assertSame(
                                DisabledBigqueryS3Copy,
                                context.getBean(BigqueryS3Copy::class.java)
                            )
                            assertInstanceOf(
                                BigqueryCopyCheckpointConsumer::class.java,
                                context.getBean(CheckpointManager::class.java).outputConsumer
                            )
                            return@use
                        }
                        val copy =
                            assertInstanceOf(
                                EnabledBigqueryS3Copy::class.java,
                                context.getBean(BigqueryS3Copy::class.java),
                            )
                        // Inspect the config held by the actual DI-created service without AWS IO.
                        val archiveConfig =
                            EnabledBigqueryS3Copy::class.java.getDeclaredField("config").let {
                                it.isAccessible = true
                                it.get(copy) as FusionConfiguration
                            }
                        assertEquals(
                            List(5) { UUID(0, 42) },
                            listOf(
                                archiveConfig.organizationId,
                                archiveConfig.workspaceId,
                                archiveConfig.sourceId,
                                archiveConfig.connectionId,
                                archiveConfig.destinationId
                            ),
                        )
                        assertEquals("platform-bucket", archiveConfig.bucket)
                        assertEquals("us-east-2", archiveConfig.region)
                        assertInstanceOf(
                            BigqueryCopyWriter::class.java,
                            context.getBean(DestinationWriter::class.java),
                        )
                        assertInstanceOf(
                            BigqueryCopyCheckpointConsumer::class.java,
                            context.getBean(CheckpointManager::class.java).outputConsumer,
                        )
                    }
                }
            }
        }
    }

    private fun context(operation: String): ApplicationContext =
        ApplicationContext.builder()
            .deduceEnvironment(false)
            .environments("connector")
            .properties(
                mapOf(
                    Operation.PROPERTY to operation,
                    "airbyte.connector.metadata.documentation-url" to
                        "https://example.com/bigquery",
                    "airbyte.destination.core.data-channel.format" to "JSONL",
                    "airbyte.destination.core.data-channel.medium" to "STDIO",
                )
            )
            .build()

    private fun specWithoutCustomerConfiguration() {
        context("spec").use { context ->
            val specification = ConnectorSpecification()
            val factory = mockk<SpecificationFactory> { every { create() } returns specification }
            val output = mockk<OutputConsumer>(relaxed = true)
            context.registerSingleton(SpecificationFactory::class.java, factory)
            context.registerSingleton(OutputConsumer::class.java, output)
            // No BigQuery config/catalog/client or archive bindings are supplied to spec.
            context.start()
            context.getBean(SpecOperation::class.java).execute()
            verify(exactly = 1) { output.accept(specification) }
        }
    }

    private fun checkInternalWrite(gcs: Boolean, raw: Boolean) {
        context("check").use { context ->
            val config = registerConnectorInputs(context, gcs, raw)
            val launcher = mockk<DestinationTaskLauncher>(relaxed = true)
            val sync = mockk<SyncManager>()
            coEvery { sync.awaitDestinationResult() } returns DestinationSuccess
            coEvery { sync.allStreamsComplete() } returns true
            context.registerSingleton(DestinationTaskLauncher::class.java, launcher)
            context.registerSingleton(SyncManager::class.java, sync)
            context.start()
            assertSame(DisabledBigqueryS3Copy, context.getBean(BigqueryS3Copy::class.java))
            assertInstanceOf(
                BigqueryCopyWriter::class.java,
                context.getBean(DestinationWriter::class.java),
            )
            assertFalse(
                context.containsBean(WriteOperation::class.java),
                "The CLI operation is still check",
            )
            assertInstanceOf(
                FreeingAnnotatingCheckpointConsumer::class.java,
                context.getBean(CheckpointManager::class.java).outputConsumer,
            )

            // Resolve the actual BigqueryBeansFactory checker. It constructs and executes its own
            // WriteOperation, although the context's command property is check. Only task execution
            // is replaced, so no database or network calls are needed to verify this operation
            // path.
            @Suppress("UNCHECKED_CAST")
            val checker =
                context.getBean(DestinationCheckerSync::class.java)
                    as DestinationCheckerSync<BigqueryConfiguration>
            checker.check(config)
            coVerify(exactly = 1) { launcher.run() }
            assertSame(DisabledBigqueryS3Copy, context.getBean(BigqueryS3Copy::class.java))
        }
    }

    private fun registerConnectorInputs(
        context: ApplicationContext,
        gcs: Boolean,
        raw: Boolean,
    ): BigqueryConfiguration {
        val json =
            com.fasterxml.jackson.databind.ObjectMapper().createObjectNode().apply {
                put("project_id", "project")
                put("job_project_id", "job-project")
                put("dataset_location", "US")
                put("dataset_id", "dataset")
                put("raw_data_dataset", "internal")
                put("disable_type_dedupe", raw)
            }
        val spec = Jsons.treeToValue(json, BigquerySpecification::class.java)
        val config =
            BigqueryConfigurationFactory()
                .makeWithoutExceptionHandling(spec)
                .copy(
                    loadingMethod =
                        if (gcs) GcsStagingConfiguration(mockk(), GcsFilePostProcessing.KEEP)
                        else BatchedStandardInsertConfiguration,
                )
        val stream =
            DestinationStream(
                "dataset",
                "check-stream",
                Append,
                ObjectTypeWithEmptySchema,
                1L,
                0L,
                1L,
                namespaceMapper = NamespaceMapper(),
            )
        context.registerSingleton(BigqueryConfiguration::class.java, config)
        context.registerSingleton(
            DestinationCatalog::class.java,
            DestinationCatalog(listOf(stream)),
        )
        context.registerSingleton(
            ConfiguredAirbyteCatalog::class.java,
            ConfiguredAirbyteCatalog().withStreams(emptyList()),
        )
        context.registerSingleton(TableCatalog::class.java, TableCatalog(emptyMap()))
        context.registerSingleton(
            TableCatalogByDescriptor::class.java,
            TableCatalogByDescriptor(emptyMap()),
        )
        context.registerSingleton(BigQuery::class.java, mockk<BigQuery>(relaxed = true))
        context.registerSingleton(
            BigQuery::class.java,
            mockk<BigQuery>(relaxed = true),
            Qualifiers.byName("jobProjectBigquery"),
        )
        return config
    }
}
