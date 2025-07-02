/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.message.DestinationRecordRaw

interface BatchEntryAssembler {

    fun assemble(record: DestinationRecordRaw): ObjectNode
}
