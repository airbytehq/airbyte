/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.kafka.format.AvroFormat;
import io.airbyte.integrations.source.kafka.format.JsonFormat;
import io.airbyte.integrations.source.kafka.format.KafkaFormat;

public class KafkaFormatFactory {

  public static KafkaFormat getFormat(final JsonNode config) {

    MessageFormat messageFormat =
        config.has("MessageFormat") ? MessageFormat.valueOf(config.get("MessageFormat").get("deserialization_type").asText().toUpperCase())
            : MessageFormat.JSON;

    switch (messageFormat) {
      case JSON -> {
        return new JsonFormat(config);
      }
      case AVRO -> {
        return new AvroFormat(config);
      }
    }
    return new JsonFormat(config);
  }

}
