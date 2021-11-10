/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

public enum JsonSchemaPrimitive {
  STRING_DATE,
  STRING_TIME,
  STRING_TIMESTAMP,
  STRING,
  NUMBER,
  OBJECT,
  ARRAY,
  BOOLEAN,
  NULL;
}
