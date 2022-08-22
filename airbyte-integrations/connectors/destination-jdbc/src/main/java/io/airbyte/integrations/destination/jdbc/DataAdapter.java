/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.function.Function;
import java.util.function.Predicate;

public class DataAdapter {

  private final Predicate<JsonNode> filterValueNode;
  private final Function<JsonNode, JsonNode> valueNodeAdapter;

  /**
   * Data adapter allows applying destination data rules. For example, Postgres destination can't
   * process text value with \u0000 unicode. You can describe filter condition for a value node and
   * function which adapts filtered value nodes.
   *
   * @param filterValueNode - filter condition which decide which value node should be adapted
   * @param valueNodeAdapter - transformation function which returns adapted value node
   */
  public DataAdapter(
                     final Predicate<JsonNode> filterValueNode,
                     final Function<JsonNode, JsonNode> valueNodeAdapter) {
    this.filterValueNode = filterValueNode;
    this.valueNodeAdapter = valueNodeAdapter;
  }

  public void adapt(final JsonNode messageData) {
    if (messageData != null) {
      adaptAllValueNodes(messageData);
    }
  }

  private void adaptAllValueNodes(final JsonNode rootNode) {
    adaptValueNodes(null, rootNode, null);
  }

  /**
   * The method inspects json node. In case, it's a value node we check the node by CheckFunction and
   * apply ValueNodeAdapter. Filtered nodes will be updated by adapted version. If element is an array
   * or an object, this we run the method recursively for them.
   *
   * @param fieldName Name of a json node
   * @param node Json node
   * @param parentNode Parent json node
   */
  private void adaptValueNodes(final String fieldName, final JsonNode node, final JsonNode parentNode) {
    if (node.isValueNode() && filterValueNode.test(node)) {
      if (fieldName != null) {
        final var adaptedNode = valueNodeAdapter.apply(node);
        ((ObjectNode) parentNode).set(fieldName, adaptedNode);
      } else
        throw new RuntimeException("Unexpected value node without fieldName. Node: " + node);
    } else if (node.isArray()) {
      node.elements().forEachRemaining(arrayNode -> adaptValueNodes(null, arrayNode, node));
    } else {
      node.fields().forEachRemaining(stringJsonNodeEntry -> adaptValueNodes(stringJsonNodeEntry.getKey(), stringJsonNodeEntry.getValue(), node));
    }
  }

}
