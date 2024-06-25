/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

/**
 * Represents a {oneOf: [...]} schema.
 *
 * This is purely a legacy type that we should eventually delete. See also [Union].
 */
data class UnsupportedOneOf(val options: List<AirbyteType>) : AirbyteType {
    override val typeName: String = TYPE

    companion object {
        const val TYPE: String = "UNSUPPORTED_ONE_OF"
    }
}
