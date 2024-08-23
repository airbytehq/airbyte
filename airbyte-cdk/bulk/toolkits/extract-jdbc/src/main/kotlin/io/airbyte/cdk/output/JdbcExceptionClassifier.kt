/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import io.airbyte.cdk.Operation
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Value
import java.sql.SQLException

@Replaces(ExceptionClassifier::class)
class JdbcExceptionClassifier(@Value("\${${Operation.PROPERTY}}") operationName: String) :
    ExceptionClassifier {

    val isCheck: Boolean = operationName == "check"

    override fun classify(e: Throwable): ConnectorError? =
        if (isCheck && e is SQLException) {
            ConfigError(sqlExceptionDisplayMessage(e))
        } else {
            null
        }

    override fun fallbackDisplayMessage(e: Throwable): String? =
        when (e) {
            is SQLException -> sqlExceptionDisplayMessage(e)
            else -> null
        }

    fun sqlExceptionDisplayMessage(e: SQLException): String =
        listOfNotNull(
                e.sqlState?.let { "State code: $it" },
                e.errorCode.takeIf { it != 0 }?.let { "Error code: $it" },
                e.message?.let { "Message: $it" },
            )
            .joinToString(separator = "; ")
}
