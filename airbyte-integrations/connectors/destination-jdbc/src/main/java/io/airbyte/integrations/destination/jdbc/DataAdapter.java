/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.function.Function;
import java.util.function.Predicate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DataAdapter {

  private static final Logger LOGGER = LoggerFactory.getLogger(DataAdapter.class);

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
                     Predicate<JsonNode> filterValueNode,
                     Function<JsonNode, JsonNode> valueNodeAdapter) {
    this.filterValueNode = filterValueNode;
    this.valueNodeAdapter = valueNodeAdapter;
  }

  public void adapt(JsonNode messageData) {
    if (messageData != null) {
      adaptAllValueNodes(messageData);
    }
  }

  private void adaptAllValueNodes(JsonNode rootNode) {
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
  private void adaptValueNodes(String fieldName, JsonNode node, JsonNode parentNode) {
    if (node.isValueNode() && filterValueNode.test(node)) {
      if (fieldName != null) {
        var adaptedNode = valueNodeAdapter.apply(node);
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
