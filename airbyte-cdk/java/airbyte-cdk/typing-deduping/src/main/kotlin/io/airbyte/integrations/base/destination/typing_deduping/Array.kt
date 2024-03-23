/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

class Array(items: AirbyteType) : AirbyteType {
    val items: AirbyteType

    init {
        this.transactions = transactions
        this.items = items
    }

    companion object {
        val typeName: String = "ARRAY"
            get() = Companion.field
    }
}
