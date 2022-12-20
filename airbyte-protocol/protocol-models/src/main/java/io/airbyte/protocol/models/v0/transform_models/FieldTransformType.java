/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.v0.transform_models;

/**
 * Types of transformations possible for a field.
 */
public enum FieldTransformType {
  ADD_FIELD,
  REMOVE_FIELD,
  UPDATE_FIELD_SCHEMA
}
