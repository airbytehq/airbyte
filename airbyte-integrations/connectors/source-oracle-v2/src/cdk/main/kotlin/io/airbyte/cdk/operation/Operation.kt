/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

const val CONNECTOR_OPERATION: String = "airbyte.connector.operation"

/** Interface that defines a CLI operation. */
fun interface Operation {

    fun execute()
}

/** Custom exception that represents a failure to execute an operation. */
class OperationExecutionException(message: String? = null, cause: Throwable? = null) :
    Exception(message, cause)
