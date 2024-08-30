/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import java.util.*

/** Debezium property manager used to build debezium properties. Implemented per connector */
interface DebeziumPropertiesManager {

    fun get(): Properties
}
