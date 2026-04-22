/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.output

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Verifies that every user-facing [CatalogValidationFailure] message surfaces a concrete
 * remediation sentence so that users can act on the failure without reading the connector source.
 */
class CatalogValidationFailureHandlerTest {

    private val streamID: StreamIdentifier =
        StreamIdentifier.from(StreamDescriptor().withName("FOO").withNamespace("PUBLIC"))

    @Test
    fun streamNotFoundIncludesRemediation() {
        val failure = StreamNotFound(streamID)
        Assertions.assertEquals(
            "Stream 'PUBLIC.FOO' not found or not accessible in source. " +
                "Restore access to it or update the connection schema to remove it from the catalog.",
            failure.message,
        )
    }

    @Test
    fun multipleStreamsFoundIncludesRemediation() {
        val failure = MultipleStreamsFound(streamID)
        Assertions.assertEquals(
            "Multiple matching streams found for 'PUBLIC.FOO' in source. " +
                "Disambiguate the stream or remove duplicates from the catalog.",
            failure.message,
        )
    }

    @Test
    fun streamHasNoFieldsIncludesRemediation() {
        val failure = StreamHasNoFields(streamID)
        Assertions.assertEquals(
            "Stream 'PUBLIC.FOO' has no accessible data fields. " +
                "Grant read access to its columns or remove the stream from the catalog.",
            failure.message,
        )
    }

    @Test
    fun fieldNotFoundIncludesRemediation() {
        val failure = FieldNotFound(streamID, "bar")
        Assertions.assertEquals(
            "Field 'bar' not found in stream 'PUBLIC.FOO'. " +
                "Remove the field from the catalog or refresh the source schema.",
            failure.message,
        )
    }

    @Test
    fun fieldTypeMismatchIncludesRemediation() {
        val failure =
            FieldTypeMismatch(
                streamID,
                "bar",
                expected = LeafAirbyteSchemaType.INTEGER,
                actual = LeafAirbyteSchemaType.STRING,
            )
        Assertions.assertEquals(
            "Field 'bar' in stream 'PUBLIC.FOO' has type STRING in source but catalog expects INTEGER. " +
                "Refresh the source schema to align the catalog with the current field type.",
            failure.message,
        )
    }

    @Test
    fun invalidPrimaryKeyIncludesRemediation() {
        val failure = InvalidPrimaryKey(streamID, listOf("id"))
        Assertions.assertEquals(
            "Primary key [id] not found in stream 'PUBLIC.FOO'. " +
                "Refresh the source schema and reselect a primary key that exists in the stream.",
            failure.message,
        )
    }

    @Test
    fun invalidCursorIncludesRemediation() {
        val failure = InvalidCursor(streamID, "updated_at")
        Assertions.assertEquals(
            "Cursor 'updated_at' not found in stream 'PUBLIC.FOO'. " +
                "Refresh the source schema and reselect a cursor field that exists in the stream.",
            failure.message,
        )
    }

    @Test
    fun invalidIncrementalSyncModeIncludesRemediation() {
        val failure = InvalidIncrementalSyncMode(streamID)
        Assertions.assertEquals(
            "Stream 'PUBLIC.FOO' has no cursor configured for incremental sync. " +
                "Configure a cursor field for incremental sync or switch the stream to full refresh.",
            failure.message,
        )
    }

    @Test
    fun errorTracePropagatesMessageWithRemediation() {
        val failure = StreamNotFound(streamID)
        val trace: AirbyteErrorTraceMessage = failure.asErrorTrace()!!
        Assertions.assertEquals(failure.message, trace.message)
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
    }

    @Test
    fun resetStreamIsNotSurfacedAsErrorTrace() {
        val failure = ResetStream(streamID)
        Assertions.assertNull(failure.asErrorTrace())
    }
}
