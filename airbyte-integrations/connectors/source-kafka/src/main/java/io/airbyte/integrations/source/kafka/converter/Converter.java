/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.converter;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

public interface Converter<V> {

  AirbyteRecordMessage convertToAirbyteRecord(String topic, V value);
}
