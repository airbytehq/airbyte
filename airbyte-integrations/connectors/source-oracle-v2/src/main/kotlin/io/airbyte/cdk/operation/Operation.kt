/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

const val CONNECTOR_OPERATION: String = "airbyte.connector.operation"

/**
 * Interface that defines a CLI operation.
 * Each operation maps to one of the available [OperationType]s.
 */
interface Operation {

    val type: OperationType

    fun execute()
}

/**
 * Defines the operations that may be invoked via the CLI arguments.
 * Not all connectors will implement all of these operations.
 */
enum class OperationType {
    SPEC,
    CHECK,
    DISCOVER,
    READ,
    WRITE,
}

/** Custom exception that represents a failure to execute an operation. */
class OperationExecutionException(message: String, cause: Throwable) : Exception(message, cause)
