/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.source

import io.airbyte.protocol.models.v0.AirbyteStream

/**
 * Stateless object for building an [AirbyteStream] during DISCOVER.
 *
 * [DefaultAirbyteStreamDecorator] is the sane default implementation, to be replaced with
 * connector-specific implementations when required.
 */
interface AirbyteStreamDecorator {
    /** Connector-specific [AirbyteStream] decoration logic for GLOBAL-state streams. */
    fun decorateGlobal(airbyteStream: AirbyteStream)

    /**
     * Connector-specific [AirbyteStream] decoration logic for STREAM-state streams for which at
     * least one discovered field can be used as a user-defined cursor in incremental syncs.
     */
    fun decorateNonGlobal(airbyteStream: AirbyteStream)

    /**
     * Connector-specific [AirbyteStream] decoration logic for STREAM-state streams for which no
     * discovered field can be used as a user-defined cursor in incremental syncs.
     */
    fun decorateNonGlobalNoCursor(airbyteStream: AirbyteStream)

    /**
     * Can the field be used as part of a primary key?
     *
     * For this to be possible,
     * 1. the field needs to be part of a key as defined by the source,
     * 2. and its values must be deserializable from the checkpoint persisted in an Airbyte state
     * message.
     *
     * This method does not determine (1), of course, because the source keys are defined in the
     * source database itself and are retrieved via [MetadataQuerier.primaryKeys]. Instead, this
     * method determines (2) based on the type information of the field, typically the [FieldType]
     * objects. For instance if the [Field.type] does not map to a [LosslessFieldType] then the
     * field can't reliably round-trip checkpoint values during a resumable initial sync.
     */
    fun isPossiblePrimaryKeyElement(field: Field): Boolean

    /**
     * Can the field be used as a cursor in a cursor-based incremental sync?
     *
     * This predicate is like [isPossiblePrimaryKeyElement] but tighter: in addition to being able
     * to round-trip the column values, we need to be able to query the max value from the source at
     * the start of the sync.
     */
    fun isPossibleCursor(field: Field): Boolean
}
