/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import com.google.cloud.bigquery.BigQuery
import io.airbyte.cdk.Operation
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
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.WriteOperation
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.spec.SpecOperation
import io.airbyte.cdk.spec.SpecificationFactory
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryRegion
import io.airbyte.integrations.destination.bigquery.spec.CdcDeletionMode
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
    fun `disabled write resolves both loading strategies and table modes without AWS configuration`() {
        runProbe("write", "false")
    }

    /**
     * The factory reads System.getenv(), not Micronaut properties. Isolate the process environment
     * instead of globally mocking configuration parsing while other connector tests run in
     * parallel.
     */
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
                .filter { it.startsWith("AIRBYTE_S3_COPY_") || it.startsWith("AWS_") }
                .toList()
                .forEach { remove(it) }
            put("AIRBYTE_S3_COPY_ENABLED", enabled)
            put("AIRBYTE_S3_COPY_ROLE_ARN", "invalid-enabled-only-field")
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
                        assertSame(
                            DisabledBigqueryS3Copy,
                            context.getBean(BigqueryS3Copy::class.java),
                        )
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
        val config =
            BigqueryConfiguration(
                "project",
                "job-project",
                BigqueryRegion.US,
                "dataset",
                if (gcs) GcsStagingConfiguration(mockk(), GcsFilePostProcessing.KEEP)
                else BatchedStandardInsertConfiguration,
                null,
                CdcDeletionMode.HARD_DELETE,
                "internal",
                raw,
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
