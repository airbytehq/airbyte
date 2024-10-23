/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.SourceConfiguration

/** An abstraction for a catalog discovery session. */
interface MetadataQuerier : AutoCloseable {

    /** Returns all available namespaces. */
    fun streamNamespaces(): List<String>

    /** Returns all available stream names in the given namespace. */
    fun streamNames(streamNamespace: String?): List<StreamIdentifier>

    /** Returns all available fields in the given stream. */
    fun fields(streamID: StreamIdentifier): List<Field>

    /** Returns the primary key for the given stream, if it exists; empty list otherwise. */
    fun primaryKey(streamID: StreamIdentifier): List<List<String>>

    /** Executes extra checks which throw a [io.airbyte.cdk.ConfigErrorException] on failure. */
    fun extraChecks()

    /** Factory for [MetadataQuerier] instances. */
    fun interface Factory<T : SourceConfiguration> {
        /** An implementation might open a connection to build a [MetadataQuerier] instance. */
        fun session(config: T): MetadataQuerier
    }

    fun commonCursorOrNull(cursorColumnID: String): FieldOrMetaField?
}
