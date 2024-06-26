/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.protocol.models.v0.StreamDescriptor

/**
 * This class should be used while upgrading a destination from V1 to V2. V2 destinations should use
 * [NoOpTyperDeduperWithV1V2Migrations] for disabling T+D, because it correctly handles various
 * migration operations.
 */
class NoopTyperDeduper : TyperDeduper {
    @Throws(Exception::class) override fun prepareSchemasAndRunMigrations() {}

    override fun prepareFinalTables() {}

    override fun typeAndDedupe(originalNamespace: String, originalName: String) {}

    override fun commitFinalTables() {}

    override fun typeAndDedupe(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>) {}

    override fun cleanup() {}
}
