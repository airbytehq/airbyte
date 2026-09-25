/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import jakarta.inject.Singleton
import java.time.OffsetDateTime

/** Slack has no CDC feed, so records carry no `_ab_cdc_*` meta fields. */
@Singleton
class SlackMetaFieldDecorator : MetaFieldDecorator {

    override val globalCursor: DataOrMetaField? = null

    override val globalMetaFields: Set<MetaField> = emptySet()

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode,
    ) {}

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload,
    ) {}
}
