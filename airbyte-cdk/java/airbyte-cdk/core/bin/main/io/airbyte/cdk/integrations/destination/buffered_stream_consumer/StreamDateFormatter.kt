/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import io.airbyte.protocol.models.v0.AirbyteMessage

/** Allows specifying transformation logic from Airbyte Json to String. */
interface StreamDateFormatter {
    fun getFormattedDate(message: AirbyteMessage?): String?
}
