/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk

/** Interface that defines a CLI operation. */
fun interface Operation {
    fun execute()

    companion object {
        const val PROPERTY: String = "airbyte.connector.operation"
    }
}
