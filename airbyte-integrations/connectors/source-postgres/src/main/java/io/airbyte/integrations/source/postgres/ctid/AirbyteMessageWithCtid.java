/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import io.airbyte.protocol.models.v0.AirbyteMessage;

/**
 * ctid of rows is queried as part of our sync and is used to checkpoint to be able to restart
 * failed sync from a known last point. Since we never want to emit a ctid it is kept in a different
 * field, to save us an expensive JsonNode.remove() operation.
 *
 * @param recordMessage row fields to emit
 * @param ctid ctid
 */
public record AirbyteMessageWithCtid(AirbyteMessage recordMessage, String ctid) {

}
