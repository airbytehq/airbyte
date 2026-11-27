/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.fasterxml.jackson.databind.JsonNode
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import io.airbyte.cdk.ConnectorUncleanExitException
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbStreamStateValue
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import org.bson.Document
import org.junit.jupiter.api.Assertions
import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.utility.DockerImageName

/**
 * Helpers shared by the read-level test classes: replica sets with MongoDB's test commands enabled
 * (so a `failCommand` failpoint can make the server fail or stall a command), catalogs built from
 * the connector's own `discover`, and views over a READ's output.
 */
object MongoDbReadTestSupport {
    /**
     * The `appName` the connector's client identifies itself with in these tests, so a failpoint
     * can target it and not the test's own client.
     */
    const val CONNECTOR_APP_NAME = "airbyte-source-mongodb-under-test"
    const val BATCH_SIZE_PROPERTY = "airbyte.connector.extract.mongodb.snapshot-batch-size"
    const val CHECKPOINT_INTERVAL_PROPERTY =
        "airbyte.connector.extract.mongodb.checkpoint-target-interval-ms"
    private const val GET_MORE_FAIL_POINT = "failGetMoreAfterCursorCheckout"
    /** [readCutAfter]: the held `getMore` must outlast the checkpoint interval. */
    const val CUT_INTERVAL_MILLIS = 1500
    const val CUT_BLOCK_MILLIS = 4000

    /** A single-node replica set of [image] with failpoints enabled. */
    fun replicaSet(image: String = "mongo:7.0"): MongoDBContainer =
        MongoDBContainer(DockerImageName.parse(image).asCompatibleSubstituteFor("mongo"))
            .withCommand("--replSet", "docker-rs", "--setParameter", "enableTestCommands=1")

    /** The connection string the connector is given: [CONNECTOR_APP_NAME] as `appName`. */
    fun connectorConnectionString(container: MongoDBContainer): String =
        "${container.connectionString}/?appName=$CONNECTOR_APP_NAME"

    fun config(
        container: MongoDBContainer,
        databases: List<String>,
        schemaEnforced: Boolean? = null,
        extraRootProperties: Map<String, Any> = emptyMap(),
    ): MongoDbSourceConfigurationSpecification =
        MongoDbTestConfigs.config(
            connectorConnectionString(container),
            databases,
            schemaEnforced = schemaEnforced,
            extraRootProperties = extraRootProperties,
        )

    /**
     * Runs [block] while the `failCommand` failpoint is active for the connector's client, then
     * disables it. [mode] is `{times: n}`, `{skip: n}` (skip the first n matching commands, fail
     * every later one) or `alwaysOn`; [data] names the commands and what to do to them (a
     * `namespace` restricts it to one collection).
     */
    fun <T> withFailPoint(
        container: MongoDBContainer,
        mode: Any,
        data: Document,
        block: () -> T,
    ): T =
        MongoClients.create(container.connectionString).use { admin: MongoClient ->
            configureFailPoint(admin, mode, data)
            try {
                block()
            } finally {
                admin
                    .getDatabase("admin")
                    .runCommand(Document("configureFailPoint", "failCommand").append("mode", "off"))
            }
        }

    private fun configureFailPoint(admin: MongoClient, mode: Any, data: Document) {
        admin
            .getDatabase("admin")
            .runCommand(
                Document("configureFailPoint", "failCommand")
                    .append("mode", mode)
                    .append("data", Document(data).append("appName", CONNECTOR_APP_NAME)),
            )
    }

    /**
     * Runs [block] while the `failGetMoreAfterCursorCheckout` failpoint fails `getMore`s with
     * [errorCode] — a failpoint of its own, so it combines with a [withFailPoint] on the same
     * command (which cannot be reconfigured while a command is held in it). It applies to every
     * client's cursors.
     */
    fun <T> withFailingGetMore(
        container: MongoDBContainer,
        mode: Document,
        errorCode: Int,
        block: () -> T,
    ): T =
        MongoClients.create(container.connectionString).use { admin: MongoClient ->
            val adminDb = admin.getDatabase("admin")
            adminDb.runCommand(
                Document("configureFailPoint", GET_MORE_FAIL_POINT)
                    .append("mode", mode)
                    .append("data", Document("errorCode", errorCode)),
            )
            try {
                block()
            } finally {
                adminDb.runCommand(
                    Document("configureFailPoint", GET_MORE_FAIL_POINT).append("mode", "off"),
                )
            }
        }

    fun times(n: Int): Document = Document("times", n)

    fun alwaysOn(): String = "alwaysOn"

    fun skip(n: Int): Document = Document("skip", n)

    /**
     * The named commands fail with [errorCode] (and [labels], which the server would normally add).
     */
    fun failing(
        vararg commands: String,
        errorCode: Int,
        labels: List<String> = emptyList(),
    ): Document =
        Document("failCommands", commands.toList()).append("errorCode", errorCode).also {
            if (labels.isNotEmpty()) it.append("errorLabels", labels)
        }

    /** The named commands are held for [millis] before the server responds. */
    fun blocking(vararg commands: String, millis: Int): Document =
        Document("failCommands", commands.toList())
            .append("blockConnection", true)
            .append("blockTimeMS", millis)

    fun discover(config: MongoDbSourceConfigurationSpecification): AirbyteCatalog =
        CliRunner.source("discover", config).run().catalogs().first()

    /** A configured catalog from the connector's own `discover`, limited to [names]. */
    fun configuredCatalog(
        config: MongoDbSourceConfigurationSpecification,
        syncMode: SyncMode,
        names: Set<String>,
    ): ConfiguredAirbyteCatalog =
        ConfiguredAirbyteCatalog()
            .withStreams(
                discover(config)
                    .streams
                    .filter { it.name in names }
                    .map { stream ->
                        ConfiguredAirbyteStream()
                            .withStream(stream)
                            .withSyncMode(syncMode)
                            .withDestinationSyncMode(
                                if (syncMode == SyncMode.INCREMENTAL) DestinationSyncMode.APPEND
                                else DestinationSyncMode.OVERWRITE,
                            )
                            .withCursorField(stream.defaultCursorField)
                            .withPrimaryKey(stream.sourceDefinedPrimaryKey)
                    },
            )

    fun read(
        config: MongoDbSourceConfigurationSpecification,
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage> = emptyList(),
    ): BufferingOutputConsumer = CliRunner.source("read", config, catalog, state).run()

    /**
     * Runs a READ whose first snapshot round of every collection is cut after [after] documents:
     * batches of that size, with the `getMore` that follows held on the server past a short
     * checkpoint interval, so the CDK cancels the round with its [after]th `_id` checkpointed and
     * the next round resumes after it. [cursors] is how many `getMore`s to hold: one per snapshot,
     * plus one for the change stream of an incremental catalog (its cold start polls once).
     */
    fun readCutAfter(
        container: MongoDBContainer,
        after: Int,
        config: MongoDbSourceConfigurationSpecification,
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage> = emptyList(),
        cursors: Int = 1,
    ): BufferingOutputConsumer =
        withSnapshotBatchSize(after) {
            withProperty(CHECKPOINT_INTERVAL_PROPERTY, CUT_INTERVAL_MILLIS.toString()) {
                withFailPoint(
                    container,
                    times(cursors),
                    blocking("getMore", millis = CUT_BLOCK_MILLIS),
                ) {
                    read(config, catalog, state)
                }
            }
        }

    /** Runs [block] with the snapshot read in batches of [size], so a `getMore` follows each. */
    fun <T> withSnapshotBatchSize(size: Int, block: () -> T): T =
        withProperty(BATCH_SIZE_PROPERTY, size.toString(), block)

    fun <T> withProperty(name: String, value: String, block: () -> T): T {
        System.setProperty(name, value)
        try {
            return block()
        } finally {
            System.clearProperty(name)
        }
    }

    /** Runs a READ that must end with an error trace; returns everything it emitted before. */
    fun readExpectingFailure(
        config: MongoDbSourceConfigurationSpecification,
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage> = emptyList(),
    ): BufferingOutputConsumer {
        val runnable: CliRunnable = CliRunner.source("read", config, catalog, state)
        Assertions.assertThrows(ConnectorUncleanExitException::class.java) { runnable.run() }
        return runnable.results
    }

    fun errors(result: BufferingOutputConsumer): List<AirbyteErrorTraceMessage> =
        result.traces().filter { it.type == AirbyteTraceMessage.Type.ERROR }.map { it.error }

    fun assertFailure(
        result: BufferingOutputConsumer,
        failureType: AirbyteErrorTraceMessage.FailureType,
        messagePart: String,
    ) {
        val errors = errors(result)
        Assertions.assertTrue(
            errors.any { it.failureType == failureType && it.message.contains(messagePart) },
            "expected a $failureType containing '$messagePart', got " +
                errors.map { "${it.failureType}: ${it.message}" },
        )
    }

    fun records(result: BufferingOutputConsumer, stream: String): List<JsonNode> =
        result.records().filter { it.stream == stream }.map { it.data }

    fun statuses(result: BufferingOutputConsumer, stream: String): List<AirbyteStreamStatus> =
        result
            .traces()
            .filter { it.type == AirbyteTraceMessage.Type.STREAM_STATUS }
            .filter { it.streamStatus.streamDescriptor.name == stream }
            .map { it.streamStatus.status }

    /** Every checkpoint emitted for [stream], in order. */
    fun streamStates(
        result: BufferingOutputConsumer,
        stream: String,
    ): List<MongoDbStreamStateValue> =
        result
            .states()
            .flatMap { it.global?.streamStates ?: listOfNotNull(it.stream) }
            .filter { it.streamDescriptor.name == stream }
            .filter { it.streamState != null && !it.streamState.isNull && !it.streamState.isEmpty }
            .map { MongoDbStreamStateValue.fromOpaqueStateValue(it.streamState) }

    /** The last checkpoint emitted for [stream], or null if none was. */
    fun lastStreamState(result: BufferingOutputConsumer, stream: String): MongoDbStreamStateValue? =
        streamStates(result, stream).lastOrNull()

    /** The resume token (`_data`) of the last GLOBAL state, or null if none was emitted. */
    fun lastResumeTokenData(result: BufferingOutputConsumer): String? =
        result
            .states()
            .mapNotNull { it.global?.sharedState }
            .lastOrNull()
            ?.get("resumeToken")
            ?.get("_data")
            ?.asText()
}
