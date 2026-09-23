/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2.readapi

import com.google.cloud.bigquery.TableDefinition
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.CreateNoPartitions
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.SocketResource
import io.airbyte.cdk.read.StateManager
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.bigqueryv2.BigQueryLongFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQuerySourceConfiguration
import io.airbyte.integrations.source.bigqueryv2.BigQuerySourceOperations
import io.airbyte.integrations.source.bigqueryv2.BigQueryTableTypes
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Instant
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Which feeds the Storage Read API factory accepts, and how the same switches drive the JDBC
 * driver's `EnableHighThroughputAPI` property. Nothing here talks to BigQuery: the table facts come
 * from the registry the metadata querier fills, and the clients are only built lazily by a creator
 * that runs.
 */
class BigQueryReadApiPartitionsCreatorFactoryTest {

    private val id = EmittedField("id", BigQueryLongFieldType)
    private val name = EmittedField("name", StringFieldType)

    private fun stream(
        table: String = "event",
        syncMode: ConfiguredSyncMode = ConfiguredSyncMode.FULL_REFRESH,
        fields: List<EmittedField> = listOf(id, name),
    ): Stream =
        Stream(
            StreamIdentifier.from(StreamDescriptor().withName(table).withNamespace("amplitude")),
            fields.toSet(),
            syncMode,
            configuredPrimaryKey = listOf(id),
            configuredCursor = if (syncMode == ConfiguredSyncMode.INCREMENTAL) id else null,
        )

    private fun config(
        useStorageReadApi: Boolean,
        availability: BigQueryReadApiAvailability,
        emulatorHost: String? = null,
    ): BigQuerySourceConfiguration =
        BigQuerySourceConfiguration(
            projectId = "p",
            credentialsJson = "{}",
            datasetId = null,
            jobProjectId = "p",
            useStorageReadApi = useStorageReadApi,
            emulatorHost = emulatorHost,
            jdbcUrlFmt = "jdbc:bigquery://x",
            baseJdbcProperties = mapOf("ProjectId" to "p"),
            maxConcurrency = 1,
            realHost = "www.googleapis.com",
            readApiAvailability = availability,
        )

    private fun factory(
        config: BigQuerySourceConfiguration,
        tableTypes: BigQueryTableTypes,
        snapshotQueries: BigQueryReadApiSnapshotQueries = FixedSnapshotQueries(upperBound = null),
        registry: BigQueryReadApiProgressRegistry = BigQueryReadApiProgressRegistry(),
    ): BigQueryReadApiPartitionsCreatorFactory =
        BigQueryReadApiPartitionsCreatorFactory(
            BigQueryReadApiClients(config),
            BigQueryReadApiConstants(),
            tableTypes,
            config.readApiAvailability,
            registry,
            ResourceAcquirer(ConcurrencyResource(1), SocketResource(null)),
            ClockFactory().fixed(),
            snapshotQueries,
        )

    private fun Stream.bootstrap(state: OpaqueStateValue? = null): StreamFeedBootstrap =
        StreamFeedBootstrap(
            outputConsumer = BufferingOutputConsumer(ClockFactory().fixed()),
            metaFieldDecorator = BigQuerySourceOperations("p"),
            stateManager = StateManager(initialStreamStates = mapOf(this to state)),
            stream = this,
            DataChannelFormat.JSONL,
            DataChannelMedium.STDIO,
            8192,
            ClockFactory().fixed(),
        )

    private fun baseTables(vararg streams: Stream): BigQueryTableTypes =
        BigQueryTableTypes().also { registry ->
            for (s in streams) {
                registry.register(
                    s.id,
                    BigQueryTableTypes.TableFacts(
                        TableDefinition.Type.TABLE,
                        552_577_444_951L,
                        275_360_099L
                    ),
                )
            }
        }

    @Test
    fun testFlagOffDeclinesAndLeavesTheDriverOnTheRestApi() {
        val availability = BigQueryReadApiAvailability()
        val config = config(useStorageReadApi = false, availability = availability)
        val event = stream()
        Assertions.assertNull(factory(config, baseTables(event)).make(event.bootstrap()))
        Assertions.assertFalse(config.jdbcProperties.containsKey("EnableHighThroughputAPI"))
    }

    @Test
    fun testUnavailableApiDeclinesAndRemovesTheDriverProperty() {
        val availability = BigQueryReadApiAvailability()
        val config = config(useStorageReadApi = true, availability = availability)
        val event = stream()
        val factory = factory(config, baseTables(event))
        Assertions.assertEquals("1", config.jdbcProperties["EnableHighThroughputAPI"])
        availability.markUnavailable("no bigquery.readsessions.create")
        Assertions.assertNull(factory.make(event.bootstrap()))
        Assertions.assertFalse(config.jdbcProperties.containsKey("EnableHighThroughputAPI"))
        Assertions.assertEquals("no bigquery.readsessions.create", availability.reason)
    }

    @Test
    fun testAvailableApiAcceptsBaseTablesInFullRefresh() {
        val config = config(useStorageReadApi = true, availability = BigQueryReadApiAvailability())
        val event = stream()
        val creator: PartitionsCreator? = factory(config, baseTables(event)).make(event.bootstrap())
        Assertions.assertTrue(creator is BigQueryReadApiPartitionsCreator, creator.toString())
        Assertions.assertEquals("1", config.jdbcProperties["EnableHighThroughputAPI"])

        // A resumable state of a live session is accepted too, ...
        val session =
            BigQueryReadSession(
                name = "projects/p/locations/us/sessions/CAIS",
                expiresAt = ClockFactory().fixed().instant().plusSeconds(3600),
                readStreams =
                    listOf(
                        "projects/p/locations/us/sessions/CAIS/streams/a",
                        "projects/p/locations/us/sessions/CAIS/streams/b"
                    ),
                arrowSchema = null,
                estimatedRowCount = null,
                estimatedBytes = null,
            )
        val inFlight = BigQueryReadApiTableProgress(session).also { it.markComplete(0) }.snapshot()
        Assertions.assertTrue(
            factory(config, baseTables(event)).make(event.bootstrap(inFlight.toOpaqueStateValue()))
                is BigQueryReadApiPartitionsCreator
        )
        // ... and a completed snapshot means there is nothing left to read.
        Assertions.assertEquals(
            CreateNoPartitions,
            factory(config, baseTables(event))
                .make(event.bootstrap(Jsons.readTree("""{"primary_key":{},"cursors":{}}"""))),
        )
    }

    @Test
    fun testViewsIncrementalEmulatorAndUnverifiedTypesAreDeclined() {
        val config = config(useStorageReadApi = true, availability = BigQueryReadApiAvailability())
        val view = stream(table = "event_view")
        val viewTypes =
            BigQueryTableTypes().also {
                it.register(
                    view.id,
                    BigQueryTableTypes.TableFacts(TableDefinition.Type.VIEW, null, null)
                )
            }
        Assertions.assertNull(factory(config, viewTypes).make(view.bootstrap()))

        val odd = stream(fields = listOf(id, EmittedField("mystery", PokemonFieldType)))
        Assertions.assertNull(factory(config, baseTables(odd)).make(odd.bootstrap()))
        Assertions.assertEquals(
            "mystery (PokemonFieldType)",
            BigQueryReadApiEligibility.unsupportedColumn(odd.fields),
        )
        Assertions.assertNull(BigQueryReadApiEligibility.unsupportedColumn(stream().fields))

        val emulated =
            config(
                useStorageReadApi = true,
                availability = BigQueryReadApiAvailability(),
                emulatorHost = "http://localhost:9050",
            )
        val event = stream()
        Assertions.assertNull(factory(emulated, baseTables(event)).make(event.bootstrap()))
    }

    @Test
    fun testIncrementalInitialSnapshotIsTakenOnThisPath() {
        val config = config(useStorageReadApi = true, availability = BigQueryReadApiAvailability())
        val incremental = stream(syncMode = ConfiguredSyncMode.INCREMENTAL)
        val queries = FixedSnapshotQueries(upperBound = Jsons.numberNode(4242L))
        val factory = factory(config, baseTables(incremental), queries)

        // No state: the snapshot is pinned (MAX(cursor) asked once, at the snapshot time).
        val creator: PartitionsCreator? = factory.make(incremental.bootstrap())
        Assertions.assertTrue(creator is BigQueryReadApiPartitionsCreator, creator.toString())
        Assertions.assertEquals(
            listOf("id" to Instant.parse("2026-09-22T08:00:00Z")),
            queries.asked,
        )

        // A completed full refresh snapshot for a now-incremental stream starts a snapshot too.
        Assertions.assertTrue(
            factory.make(
                incremental.bootstrap(Jsons.readTree("""{"primary_key":{},"cursors":{}}"""))
            ) is BigQueryReadApiPartitionsCreator
        )

        // An own in-flight snapshot state with the bound resumes on this path ...
        val session =
            BigQueryReadSession(
                name = "projects/p/locations/us/sessions/CAIS",
                expiresAt = ClockFactory().fixed().instant().plusSeconds(3600),
                readStreams = listOf("projects/p/locations/us/sessions/CAIS/streams/a"),
                arrowSchema = null,
                estimatedRowCount = null,
                estimatedBytes = null,
            )
        val bound = BigQueryReadApiState.CursorBound("id", Jsons.numberNode(4242L))
        val snapshotTime = Instant.parse("2026-09-22T07:59:58Z")
        val inFlight =
            BigQueryReadApiTableProgress(
                    session,
                    snapshotTime = snapshotTime,
                    cursorUpperBound = bound
                )
                .snapshot()
        Assertions.assertTrue(
            factory.make(incremental.bootstrap(inFlight.toOpaqueStateValue()))
                is BigQueryReadApiPartitionsCreator
        )
        // ... and a complete one emits the toolkit's cursor checkpoint as its terminal state.
        val complete =
            BigQueryReadApiTableProgress(
                    session,
                    snapshotTime = snapshotTime,
                    cursorUpperBound = bound
                )
                .also { it.markComplete(0) }
                .snapshot()
        val completeCreator: PartitionsCreator? =
            factory.make(incremental.bootstrap(complete.toOpaqueStateValue()))
        Assertions.assertTrue(completeCreator is BigQueryReadApiPartitionsCreator)
        val readers = runBlocking { completeCreator!!.run() }
        Assertions.assertEquals(1, readers.size)
        // Re-parsed, so that integer node classes do not matter.
        Assertions.assertEquals(
            Jsons.readTree("""{"primary_key":{},"cursors":{"id":4242}}"""),
            Jsons.readTree(
                Jsons.writeValueAsString(readers.single().checkpoint().opaqueStateValue)
            ),
        )
        Assertions.assertEquals(
            DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(id, Jsons.numberNode(4242L)),
            readers.single().checkpoint().opaqueStateValue,
        )
    }

    @Test
    fun testIncrementalStatesOfTheQueryApiAreDeclined() {
        val config = config(useStorageReadApi = true, availability = BigQueryReadApiAvailability())
        val incremental = stream(syncMode = ConfiguredSyncMode.INCREMENTAL)
        val queries = FixedSnapshotQueries(upperBound = Jsons.numberNode(4242L))
        val factory = factory(config, baseTables(incremental), queries)
        // A cursor checkpoint: the deltas are the query API's.
        Assertions.assertNull(
            factory.make(
                incremental.bootstrap(Jsons.readTree("""{"primary_key":{},"cursors":{"id":5}}"""))
            )
        )
        // A query API snapshot in progress.
        Assertions.assertNull(
            factory.make(
                incremental.bootstrap(
                    Jsons.readTree("""{"primary_key":{"id":3},"cursors":{"id":9}}""")
                )
            )
        )
        // A legacy source-bigquery state.
        Assertions.assertNull(
            factory.make(
                incremental.bootstrap(
                    Jsons.readTree("""{"stream_name":"event","cursor_field":["id"],"cursor":"3"}""")
                )
            )
        )
        Assertions.assertTrue(queries.asked.isEmpty(), "no MAX query for declined streams")

        // An empty table (no cursor value) is left to the query API too.
        val empty = FixedSnapshotQueries(upperBound = null)
        Assertions.assertNull(
            factory(config, baseTables(incremental), empty).make(incremental.bootstrap())
        )
        Assertions.assertEquals(1, empty.asked.size)

        // A cursor of a type this path does not snapshot.
        val blob = EmittedField("blob", BytesFieldType)
        val oddCursor =
            Stream(
                incremental.id,
                setOf(id, blob),
                ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(id),
                configuredCursor = blob,
            )
        Assertions.assertNull(
            factory(config, baseTables(oddCursor), queries).make(oddCursor.bootstrap())
        )
    }

    @Test
    fun testATableCompletedInThisSyncIsNotReadAgainByAnyPath() {
        val config = config(useStorageReadApi = true, availability = BigQueryReadApiAvailability())
        val incremental = stream(syncMode = ConfiguredSyncMode.INCREMENTAL)
        val session =
            BigQueryReadSession(
                name = "projects/p/locations/us/sessions/CAIS",
                expiresAt = ClockFactory().fixed().instant().plusSeconds(3600),
                readStreams = listOf("projects/p/locations/us/sessions/CAIS/streams/a"),
                arrowSchema = null,
                estimatedRowCount = null,
                estimatedBytes = null,
            )
        val registry = BigQueryReadApiProgressRegistry()
        registry.put(
            incremental.id,
            BigQueryReadApiTableProgress(
                    session,
                    snapshotTime = Instant.parse("2026-09-22T07:59:58Z"),
                    cursorUpperBound =
                        BigQueryReadApiState.CursorBound("id", Jsons.numberNode(4242L)),
                )
                .also { it.markComplete(0) },
        )
        val queries = FixedSnapshotQueries(upperBound = Jsons.numberNode(4242L))
        // Round 2 of the same READ: the terminal cursor checkpoint is the current state; without
        // the registry this would be declined and the query API would re-read the boundary rows.
        Assertions.assertEquals(
            CreateNoPartitions,
            factory(config, baseTables(incremental), queries, registry)
                .make(
                    incremental.bootstrap(
                        Jsons.readTree("""{"primary_key":{},"cursors":{"id":4242}}""")
                    )
                ),
        )
        Assertions.assertTrue(queries.asked.isEmpty())
        // Same for a full refresh table whose terminal state is out.
        val fullRefresh = stream()
        registry.put(
            fullRefresh.id,
            BigQueryReadApiTableProgress(session).also { it.markComplete(0) },
        )
        Assertions.assertEquals(
            CreateNoPartitions,
            factory(config, baseTables(fullRefresh), queries, registry)
                .make(fullRefresh.bootstrap(Jsons.readTree("""{"primary_key":{},"cursors":{}}"""))),
        )
    }
}
