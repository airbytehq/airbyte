/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.util;

import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ContainerNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.math.BigDecimal;

public class JsonUtil {

  private static final String ERROR_MESSAGE = "Can't populate the node type : ";

  public static void putBooleanValueIntoJson(final ContainerNode<?> node, final boolean value, final String fieldName) {
    if (node instanceof ArrayNode) {
      ((ArrayNode) node).add(value);
    } else if (node instanceof ObjectNode) {
      ((ObjectNode) node).put(fieldName, value);
    } else {
      throw new RuntimeException(ERROR_MESSAGE + node.getClass().getName());
    }
  }

  public static void putLongValueIntoJson(final ContainerNode<?> node, final long value, final String fieldName) {
    if (node instanceof ArrayNode) {
      ((ArrayNode) node).add(value);
    } else if (node instanceof ObjectNode) {
      ((ObjectNode) node).put(fieldName, value);
    } else {
      throw new RuntimeException(ERROR_MESSAGE + node.getClass().getName());
    }
  }

  public static void putDoubleValueIntoJson(final ContainerNode<?> node, final double value, final String fieldName) {
    if (node instanceof ArrayNode) {
      ((ArrayNode) node).add(value);
    } else if (node instanceof ObjectNode) {
      ((ObjectNode) node).put(fieldName, value);
    } else {
      throw new RuntimeException(ERROR_MESSAGE + node.getClass().getName());
    }
  }

  public static void putBigDecimalValueIntoJson(final ContainerNode<?> node, final BigDecimal value, final String fieldName) {
    if (node instanceof ArrayNode) {
      ((ArrayNode) node).add(value);
    } else if (node instanceof ObjectNode) {
      ((ObjectNode) node).put(fieldName, value);
    } else {
      throw new RuntimeException(ERROR_MESSAGE + node.getClass().getName());
    }
  }

  public static void putStringValueIntoJson(final ContainerNode<?> node, final String value, final String fieldName) {
    if (node instanceof ArrayNode) {
      ((ArrayNode) node).add(value);
    } else if (node instanceof ObjectNode) {
      ((ObjectNode) node).put(fieldName, value);
    } else {
      throw new RuntimeException(ERROR_MESSAGE + node.getClass().getName());
    }
  }

  public static void putBytesValueIntoJson(final ContainerNode<?> node, final byte[] value, final String fieldName) {
    if (node instanceof ArrayNode) {
      ((ArrayNode) node).add(value);
    } else if (node instanceof ObjectNode) {
      ((ObjectNode) node).put(fieldName, value);
    } else {
      throw new RuntimeException(ERROR_MESSAGE + node.getClass().getName());
    }
  }

}
