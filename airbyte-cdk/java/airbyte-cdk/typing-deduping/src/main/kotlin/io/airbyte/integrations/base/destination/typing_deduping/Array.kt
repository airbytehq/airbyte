/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

data class Array(val items: AirbyteType) : AirbyteType {
    override val typeName: String = TYPE

    companion object {
        const val TYPE: String = "ARRAY"
    }
}
