/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.util.function.Predicate;
import kotlin.Pair;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class PostgresDataTransformer implements StreamAwareDataTransformer {

  /*
   * This class is copied in its entirety from DataAdapter class to unify logic into one single
   * transformer invocation before serializing to string in AsyncStreamConsumer.
   */

  final Predicate<JsonNode> filterValueNode;
  final Function<JsonNode, JsonNode> valueNodeAdapter;

  public PostgresDataTransformer() {
    this.filterValueNode = jsonNode -> jsonNode.isTextual() && jsonNode.textValue().contains("\u0000");
    this.valueNodeAdapter = jsonNode -> {
      final String textValue = jsonNode.textValue().replaceAll("\\u0000", "");
      return Jsons.jsonNode(textValue);
    };
  }

  @NotNull
  @Override
  public Pair<JsonNode, AirbyteRecordMessageMeta> transform(@Nullable StreamDescriptor streamDescriptor,
                                                            @Nullable JsonNode data,
                                                            @Nullable AirbyteRecordMessageMeta meta) {
    final List<AirbyteRecordMessageMetaChange> metaChanges = new ArrayList<>();
    if (meta != null && meta.getChanges() != null) {
      metaChanges.addAll(meta.getChanges());
    }
    // Does inplace changes in the actual JsonNode reference.
    adapt(data);
    return new Pair<>(data, new AirbyteRecordMessageMeta().withChanges(metaChanges));
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
