/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

/** @param properties Use LinkedHashMap to preserve insertion order. */
data class Struct(val properties: LinkedHashMap<String, AirbyteType>) : AirbyteType {
    override val typeName: String = TYPE

    companion object {
        const val TYPE: String = "STRUCT"
    }
}
