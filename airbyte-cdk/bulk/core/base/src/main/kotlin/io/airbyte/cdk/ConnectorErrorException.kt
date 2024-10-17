/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk

/**
 * A [ConnectorErrorException] is an exception which readily maps to an
 * [io.airbyte.cdk.output.ConnectorError] object.
 */
sealed class ConnectorErrorException(
    displayMessage: String?,
    exception: Throwable?,
) : RuntimeException(displayMessage, exception)

/** See [io.airbyte.cdk.output.ConfigError]. */
class ConfigErrorException(
    displayMessage: String,
    exception: Throwable? = null,
) : ConnectorErrorException(displayMessage, exception)

/** See [io.airbyte.cdk.output.TransientError]. */
class TransientErrorException(
    displayMessage: String,
    exception: Throwable? = null,
) : ConnectorErrorException(displayMessage, exception)

/** See [io.airbyte.cdk.output.SystemError]. */
class SystemErrorException(
    displayMessage: String?,
    exception: Throwable? = null,
) : ConnectorErrorException(displayMessage, exception)
