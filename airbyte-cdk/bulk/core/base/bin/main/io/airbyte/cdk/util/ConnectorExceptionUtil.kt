/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.util

object ConnectorExceptionUtil {
    val HTTP_AUTHENTICATION_ERROR_CODES: List<Int> = listOf(401, 403)
}
