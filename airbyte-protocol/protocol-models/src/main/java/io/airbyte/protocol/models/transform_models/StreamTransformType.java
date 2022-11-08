/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.transform_models;

/**
 * Types of transformations possible for a stream.
 */
public enum StreamTransformType {
  ADD_STREAM,
  REMOVE_STREAM,
  UPDATE_STREAM
}
