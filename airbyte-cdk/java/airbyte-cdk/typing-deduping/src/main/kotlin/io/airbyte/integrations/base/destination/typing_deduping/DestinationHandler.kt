/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

interface DestinationHandler<DestinationState> {
    @Throws(Exception::class) fun execute(sql: Sql)

    /**
     * Fetch the current state of the destination for the given streams. This method MUST create the
     * airbyte_internal.state table if it does not exist. This method MAY assume the
     * airbyte_internal schema already exists. (substitute the appropriate raw table schema if the
     * user is overriding it).
     */
    @Throws(Exception::class)
    fun gatherInitialState(
        streamConfigs: List<StreamConfig>
    ): List<DestinationInitialStatus<DestinationState>>

    @Throws(Exception::class)
    fun commitDestinationStates(destinationStates: Map<StreamId, DestinationState>)

    /**
     * Create all required namespaces required for the Sync. Implementations may optimize for
     * checking if schema exists already.
     *
     * This exists here instead of StorageOperations to avoid issuing create namespace call for
     * every stream and instead called from Sync operation with distinct set of namespaces required
     * within the sync.
     */
    fun createNamespaces(schemas: Set<String>)
}
