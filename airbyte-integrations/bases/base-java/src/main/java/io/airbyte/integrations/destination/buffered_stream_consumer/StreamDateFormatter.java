/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.protocol.models.AirbyteMessage;

/**
 * Allows specifying transformation logic from Airbyte Json to String.
 */
public interface StreamDateFormatter {

  String getFormattedDate(AirbyteMessage airbyteMessage);

}
