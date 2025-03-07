/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.probably_core_stuff

import com.google.common.collect.ImmutableList

object ConnectorExceptionUtil {
    val HTTP_AUTHENTICATION_ERROR_CODES: List<Int> = ImmutableList.of(401, 403)
}
