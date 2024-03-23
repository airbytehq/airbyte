/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

/**
 * @param properties Use LinkedHashMap to preserve insertion order.
 */
class Struct(properties: LinkedHashMap<String, AirbyteType>) : AirbyteType {
    val properties: LinkedHashMap<String, AirbyteType>

    init {
        this.transactions = transactions
        this.items = items
        this.properties = properties
    }

    companion object {
        val typeName: String = "STRUCT"
            get() = Companion.field
    }
}
