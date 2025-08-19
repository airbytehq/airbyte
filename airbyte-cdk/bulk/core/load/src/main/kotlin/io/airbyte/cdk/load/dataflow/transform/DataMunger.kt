/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordRaw

interface DataMunger {
    fun transformForDest(msg: DestinationRecordRaw): Map<String, AirbyteValue>
}
