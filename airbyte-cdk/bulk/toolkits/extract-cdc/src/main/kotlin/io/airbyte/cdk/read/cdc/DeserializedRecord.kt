/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.FieldValueChange

/** [DeserializedRecord]s are used to generate Airbyte RECORD messages. */
data class DeserializedRecord(
    val data: NativeRecordPayload,
    val changes: Map<Field, FieldValueChange>,
)
