/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

/**
 * message format in kafka queue
 * https://docs.confluent.io/platform/current/schema-registry/serdes-develop/index.html
 */
public enum MessageFormat {
  JSON,
  AVRO
}
