/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import java.util.*

/**
 * Debezium manager used to build debezium properties, and read state from debezium files.
 * Implemented per connector
 */
interface DebeziumManager {

    fun getPropertiesForSync(opaqueStateValue: OpaqueStateValue?): Properties
    fun getPropertiesForSchemaHistory(): Properties
    fun readOffsetState(): OpaqueStateValue
}
