/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQueryException
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.ConnectorExceptionUtil

internal fun BigQueryException.toConfigExceptionIfNeeded(): Exception =
    if (
        ConnectorExceptionUtil.HTTP_AUTHENTICATION_ERROR_CODES.contains(code) &&
            error?.reason != "rateLimitExceeded"
    ) {
        ConfigErrorException(message!!, this)
    } else {
        this
    }
