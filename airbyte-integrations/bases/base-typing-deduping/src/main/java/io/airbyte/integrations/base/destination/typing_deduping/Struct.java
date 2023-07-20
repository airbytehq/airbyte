/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.LinkedHashMap;

/**
 * @param properties Use LinkedHashMap to preserve insertion order.
 */
public record Struct(LinkedHashMap<String, AirbyteType> properties) implements AirbyteType {

}
