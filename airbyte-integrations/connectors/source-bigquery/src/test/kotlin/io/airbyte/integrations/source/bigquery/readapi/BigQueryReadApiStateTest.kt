/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.SocketResource
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.bigquery.BigQueryDateTimeFieldType
import io.airbyte.integrations.source.bigquery.BigQueryLongFieldType
import io.airbyte.integrations.source.bigquery.BigQuerySourceConfiguration
import io.airbyte.integrations.source.bigquery.BigQueryTableTypes
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BigQueryReadApiStateTest {

    private val session =
        BigQueryReadSession(
            name = "projects/p/locations/us/sessions/CAIS",
            expiresAt = Instant.parse("2026-09-22T10:28:18Z"),
            readStreams = (0 until 5).map { "projects/p/locations/us/sessions/CAIS/streams/s$it" },
            arrowSchema = null,
            estimatedRowCount = 275_360_099L,
            estimatedBytes = 552_000_000_000L,
        )

    @Test
    fun testProgressSnapshotIsAWatermarkPlusOutOfOrderProgress() {
        val progress = BigQueryReadApiTableProgress(session)
        progress.markComplete(0)
        progress.markComplete(1)
        progress.recordRows(2, 1_300_000L)
        progress.markComplete(3)
        Assertions.assertFalse(progress.isComplete)

        val state: BigQueryReadApiState = progress.snapshot()
        Assertions.assertEquals(1, state.completedThrough)
        Assertions.assertEquals(listOf(3), state.complete)
        Assertions.assertEquals(mapOf("2" to 1_300_000L), state.offsets)
        Assertions.assertEquals(
            listOf(
                BigQueryReadApiState.ReadStreamWork(2, session.readStreams[2], 1_300_000L),
                BigQueryReadApiState.ReadStreamWork(4, session.readStreams[4], 0L),
            ),
            state.remainingWork(),
        )
        Assertions.assertEquals(state.remainingWork(), progress.remainingWork())

        // Re-parsed, so that integer node classes do not matter.
        val json: JsonNode = Jsons.readTree(Jsons.writeValueAsString(state.toOpaqueStateValue()))
        Assertions.assertEquals(
            Jsons.readTree(
                """{"bigquery_read_session":{"name":"projects/p/locations/us/sessions/CAIS",
                   "expires_at":"2026-09-22T10:28:18Z",
                   "bigquery_read_streams":["projects/p/locations/us/sessions/CAIS/streams/s0",
                     "projects/p/locations/us/sessions/CAIS/streams/s1",
                     "projects/p/locations/us/sessions/CAIS/streams/s2",
                     "projects/p/locations/us/sessions/CAIS/streams/s3",
                     "projects/p/locations/us/sessions/CAIS/streams/s4"]},
                   "bigquery_read_streams_completed_through":1,
                   "bigquery_read_streams_complete":[3],
                   "bigquery_read_stream_offsets":{"2":1300000}}"""
            ),
            json,
        )
        // The word "stream" never appears on its own in the state: it is an Airbyte term.
        for (key in json.fieldNames().asSequence().toList()) {
            Assertions.assertTrue(key.startsWith("bigquery_read_"), key)
        }
        Assertions.assertEquals(state, BigQueryReadApiState.parseOrNull(json))

        // Resuming from that state in a fresh process restores the same progress.
        val resumed = BigQueryReadApiTableProgress(session, state)
        Assertions.assertEquals(state, resumed.snapshot())
        resumed.markComplete(2)
        resumed.markComplete(4)
        Assertions.assertTrue(resumed.isComplete)
        Assertions.assertEquals(4, resumed.snapshot().completedThrough)
        Assertions.assertTrue(resumed.snapshot().isComplete)
    }

    @Test
    fun testFreshAndEmptySessions() {
        val fresh = BigQueryReadApiTableProgress(session).snapshot()
        Assertions.assertEquals(-1, fresh.completedThrough)
        Assertions.assertTrue(fresh.complete.isEmpty() && fresh.offsets.isEmpty())
        Assertions.assertEquals(5, fresh.remainingWork().size)
        // Optional fields are omitted from the JSON.
        Assertions.assertEquals(
            setOf("bigquery_read_session", "bigquery_read_streams_completed_through"),
            fresh.toOpaqueStateValue().fieldNames().asSequence().toSet(),
        )
        val empty = BigQueryReadApiTableProgress(session.copy(readStreams = emptyList()))
        Assertions.assertTrue(empty.isComplete)
        Assertions.assertTrue(empty.snapshot().isComplete)
    }

    @Test
    fun testOtherStateShapesAreNotReadApiStates() {
        Assertions.assertNull(BigQueryReadApiState.parseOrNull(null))
        Assertions.assertNull(BigQueryReadApiState.parseOrNull(Jsons.nullNode()))
        Assertions.assertNull(
            BigQueryReadApiState.parseOrNull(Jsons.readTree("""{"primary_key":{},"cursors":{}}"""))
        )
        Assertions.assertNull(
            BigQueryReadApiState.parseOrNull(
                Jsons.readTree("""{"stream_name":"t","cursor_field":["id"],"cursor":"3"}""")
            )
        )
        Assertions.assertNull(
            BigQueryReadApiState.parseOrNull(Jsons.readTree("""{"bigquery_read_session":null}"""))
        )
    }

    @Test
    fun testPlan() {
        val now: Instant = Instant.parse("2026-09-22T08:00:00Z")
        val factory: BigQueryReadApiPartitionsCreatorFactory =
            factory(Clock.fixed(now, ZoneOffset.UTC))
        val stream =
            Stream(
                StreamIdentifier.from(
                    StreamDescriptor().withName("event").withNamespace("amplitude")
                ),
                setOf(EmittedField("id", BigQueryLongFieldType)),
                ConfiguredSyncMode.FULL_REFRESH,
                configuredPrimaryKey = listOf(EmittedField("id", BigQueryLongFieldType)),
                configuredCursor = null,
            )
        Assertions.assertEquals(
            BigQueryReadApiPlan.Fresh("no prior state"),
            factory.plan(stream, null),
        )
        val inFlight: BigQueryReadApiState =
            BigQueryReadApiTableProgress(session).also { it.markComplete(0) }.snapshot()
        Assertions.assertEquals(
            BigQueryReadApiPlan.Resume(inFlight),
            factory.plan(stream, inFlight.toOpaqueStateValue()),
        )
        val complete: BigQueryReadApiState =
            BigQueryReadApiTableProgress(session)
                .also { p -> (0 until 5).forEach { p.markComplete(it) } }
                .snapshot()
        Assertions.assertEquals(
            BigQueryReadApiPlan.Complete,
            factory.plan(stream, complete.toOpaqueStateValue()),
        )
        val expired: BigQueryReadApiState =
            inFlight.copy(session = inFlight.session.copy(expiresAt = "2026-09-22T07:59:59Z"))
        Assertions.assertTrue(
            factory.plan(stream, expired.toOpaqueStateValue()) is BigQueryReadApiPlan.Fresh
        )
        // The extract-jdbc toolkit's completed snapshot: nothing left to do.
        Assertions.assertEquals(
            BigQueryReadApiPlan.Complete,
            factory.plan(stream, Jsons.readTree("""{"primary_key":{},"cursors":{}}""")),
        )
        // A mid-way query-API state or a legacy state: start over on this path.
        Assertions.assertTrue(
            factory.plan(stream, Jsons.readTree("""{"primary_key":{"id":123},"cursors":{}}"""))
                is BigQueryReadApiPlan.Fresh
        )
        Assertions.assertTrue(
            factory.plan(
                stream,
                Jsons.readTree("""{"stream_name":"event","cursor_field":["id"],"cursor":"3"}""")
            ) is BigQueryReadApiPlan.Fresh
        )
    }

    private fun factory(clock: Clock): BigQueryReadApiPartitionsCreatorFactory {
        val config =
            BigQuerySourceConfiguration(
                projectId = "p",
                credentialsJson = "{}",
                datasetId = null,
                jobProjectId = "p",
                useStorageReadApi = true,
                emulatorHost = null,
                jdbcUrlFmt = "jdbc:bigquery://x",
                baseJdbcProperties = emptyMap(),
                maxConcurrency = 1,
                realHost = "www.googleapis.com",
            )
        return BigQueryReadApiPartitionsCreatorFactory(
            BigQueryReadApiClients(config),
            BigQueryReadApiConstants(),
            BigQueryTableTypes(),
            BigQueryReadApiAvailability(),
            BigQueryReadApiProgressRegistry(),
            ResourceAcquirer(ConcurrencyResource(1), SocketResource(null)),
            clock,
            FixedSnapshotQueries(upperBound = null),
        )
    }

    @Test
    fun testIncrementalSnapshotFieldsRoundTripAndDrivePlanning() {
        val bound =
            BigQueryReadApiState.CursorBound(
                "updated_at",
                Jsons.textNode("2024-01-10T20:53:31.000000")
            )
        val snapshotTime = Instant.parse("2026-09-22T07:59:58.123456Z")
        val progress =
            BigQueryReadApiTableProgress(
                session,
                snapshotTime = snapshotTime,
                cursorUpperBound = bound
            )
        progress.markComplete(0)
        val state: BigQueryReadApiState = progress.snapshot()
        val json: JsonNode = Jsons.readTree(Jsons.writeValueAsString(state.toOpaqueStateValue()))
        Assertions.assertEquals(
            "2026-09-22T07:59:58.123456Z",
            json["bigquery_read_snapshot_time"].asText()
        )
        Assertions.assertEquals(
            Jsons.readTree("""{"cursor":"updated_at","value":"2024-01-10T20:53:31.000000"}"""),
            json["bigquery_read_cursor_upper_bound"],
        )
        val parsed: BigQueryReadApiState = BigQueryReadApiState.parseOrNull(json)!!
        Assertions.assertEquals(snapshotTime, parsed.snapshotTimeInstant)
        Assertions.assertEquals(bound, parsed.cursorUpperBound)
        // Resumed progress carries them on.
        val resumed = BigQueryReadApiTableProgress(session, parsed)
        Assertions.assertEquals(snapshotTime, resumed.snapshotTime)
        Assertions.assertEquals(bound, resumed.cursorUpperBound)
        Assertions.assertEquals(bound, resumed.snapshot().cursorUpperBound)
        // A full refresh state has neither field.
        val fullRefresh: JsonNode =
            Jsons.readTree(
                Jsons.writeValueAsString(
                    BigQueryReadApiTableProgress(session).snapshot().toOpaqueStateValue()
                )
            )
        Assertions.assertFalse(fullRefresh.has("bigquery_read_snapshot_time"))
        Assertions.assertFalse(fullRefresh.has("bigquery_read_cursor_upper_bound"))

        val now: Instant = Instant.parse("2026-09-22T08:00:00Z")
        val factory: BigQueryReadApiPartitionsCreatorFactory =
            factory(Clock.fixed(now, ZoneOffset.UTC))
        val updatedAt = EmittedField("updated_at", BigQueryDateTimeFieldType)
        val incremental =
            Stream(
                StreamIdentifier.from(
                    StreamDescriptor().withName("users").withNamespace("rodi_proto_type_test")
                ),
                setOf(EmittedField("id", BigQueryLongFieldType), updatedAt),
                ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(EmittedField("id", BigQueryLongFieldType)),
                configuredCursor = updatedAt,
            )
        // In flight and live: resume.
        Assertions.assertEquals(
            BigQueryReadApiPlan.Resume(parsed),
            factory.plan(incremental, json),
        )
        // Expired: a fresh plan that keeps the snapshot time and the bound.
        val expired: BigQueryReadApiState =
            parsed.copy(session = parsed.session.copy(expiresAt = "2026-09-22T07:59:59Z"))
        val plan: BigQueryReadApiPlan = factory.plan(incremental, expired.toOpaqueStateValue())
        Assertions.assertTrue(plan is BigQueryReadApiPlan.Fresh, plan.toString())
        Assertions.assertEquals(
            BigQueryReadApiSnapshotSpec(snapshotTime, bound, fromExpiredSession = true),
            (plan as BigQueryReadApiPlan.Fresh).snapshot,
        )
        // An own state without the bound (or for another cursor): start over.
        val unbounded: BigQueryReadApiState =
            parsed.copy(snapshotTime = null, cursorUpperBound = null)
        Assertions.assertTrue(
            factory.plan(incremental, unbounded.toOpaqueStateValue()) is BigQueryReadApiPlan.Fresh
        )
        val otherCursor: BigQueryReadApiState =
            parsed.copy(
                cursorUpperBound = BigQueryReadApiState.CursorBound("id", Jsons.numberNode(1))
            )
        Assertions.assertTrue(
            factory.plan(incremental, otherCursor.toOpaqueStateValue()) is BigQueryReadApiPlan.Fresh
        )
        // The query API's cursor checkpoint and its snapshot in progress: not this path's.
        Assertions.assertTrue(
            factory.plan(
                incremental,
                Jsons.readTree(
                    """{"primary_key":{},"cursors":{"updated_at":"2024-01-03T00:00:00.000000"}}"""
                )
            ) is BigQueryReadApiPlan.Decline
        )
        Assertions.assertTrue(
            factory.plan(
                incremental,
                Jsons.readTree(
                    """{"primary_key":{"id":7},"cursors":{"updated_at":"2024-01-03T00:00:00.000000"}}"""
                )
            ) is BigQueryReadApiPlan.Decline
        )
        Assertions.assertTrue(
            factory.plan(
                incremental,
                Jsons.readTree(
                    """{"stream_name":"users","cursor_field":["updated_at"],"cursor":"2024-01-03T00:00:00Z"}"""
                )
            ) is BigQueryReadApiPlan.Decline
        )
        // A completed full refresh snapshot: the incremental snapshot starts over.
        Assertions.assertEquals(
            BigQueryReadApiPlan.Fresh("a completed full refresh snapshot"),
            factory.plan(incremental, Jsons.readTree("""{"primary_key":{},"cursors":{}}""")),
        )
    }
}
