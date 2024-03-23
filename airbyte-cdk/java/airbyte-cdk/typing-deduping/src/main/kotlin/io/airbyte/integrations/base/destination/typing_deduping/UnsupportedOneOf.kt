/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

/**
 * Represents a {oneOf: [...]} schema.
 *
 *
 * This is purely a legacy type that we should eventually delete. See also [Union].
 */
@JvmRecord
data class UnsupportedOneOf(val options: List<AirbyteType>) : AirbyteType {
    override fun getTypeName(): String {
        return TYPE
    }

    companion object {
        const val TYPE: String = "UNSUPPORTED_ONE_OF"
    }
}
