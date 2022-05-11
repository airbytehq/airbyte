/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

public enum JsonSchemaPrimitive {

  STRING,
  NUMBER,
  OBJECT,
  ARRAY,
  BOOLEAN,
  //SWE 265 Pull Request 1
  INTEGER,
  NULL;

}
