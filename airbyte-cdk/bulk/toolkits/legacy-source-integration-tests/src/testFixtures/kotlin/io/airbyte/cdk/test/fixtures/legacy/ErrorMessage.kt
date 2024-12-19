/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import java.util.*

object ErrorMessage {
    // TODO: this could be built using a Builder design pattern instead of passing in 0 to indicate
    // no
    // errorCode exists
    @JvmStatic
    fun getErrorMessage(
        stateCode: String?,
        errorCode: Int,
        message: String?,
        exception: Exception
    ): String {
        return if (Objects.isNull(message)) {
            configMessage(stateCode, 0, exception.message)
        } else {
            configMessage(stateCode, errorCode, message)
        }
    }

    private fun configMessage(stateCode: String?, errorCode: Int, message: String?): String {
        val stateCodePart =
            if (Objects.isNull(stateCode)) "" else String.format("State code: %s; ", stateCode)
        val errorCodePart = if (errorCode == 0) "" else String.format("Error code: %s; ", errorCode)
        return String.format("%s%sMessage: %s", stateCodePart, errorCodePart, message)
    }
}
