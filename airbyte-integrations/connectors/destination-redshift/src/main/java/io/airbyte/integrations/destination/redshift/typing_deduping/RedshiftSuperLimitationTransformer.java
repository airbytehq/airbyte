/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import kotlin.Pair;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.jetbrains.annotations.NotNull;

@Slf4j
public class RedshiftSuperLimitationTransformer implements StreamAwareDataTransformer {

  private record ScalarNodeModification(int size, int removedSize, boolean shouldNull) {}

  public record TransformationInfo(int originalBytes, int removedBytes, JsonNode node, AirbyteRecordMessageMeta meta) {}

  public static final int REDSHIFT_VARCHAR_MAX_BYTE_SIZE = 65535;
  public static final int REDSHIFT_SUPER_MAX_BYTE_SIZE = 16 * 1024 * 1024;

  static final Predicate<String> DEFAULT_PREDICATE_VARCHAR_GREATER_THAN_64K = text -> getByteSize(text) > REDSHIFT_VARCHAR_MAX_BYTE_SIZE;
  static final Predicate<Integer> DEFAULT_PREDICATE_RECORD_SIZE_GT_THAN_16M = size -> size > REDSHIFT_SUPER_MAX_BYTE_SIZE;

  private static final int CURLY_BRACES_BYTE_SIZE = getByteSize("{}");
  private static final int SQUARE_BRACKETS_BYTE_SIZE = getByteSize("[]");
  private static final int OBJECT_COLON_QUOTES_COMMA_BYTE_SIZE = getByteSize("\"\":,");

  private final ParsedCatalog parsedCatalog;

  private final String defaultNamespace;

  public RedshiftSuperLimitationTransformer(final ParsedCatalog parsedCatalog, final String defaultNamespace) {
    this.parsedCatalog = parsedCatalog;
    Objects.requireNonNull(defaultNamespace);
    this.defaultNamespace = defaultNamespace;

  }

  /*
   * This method walks the Json tree nodes and does the following
   *
   * 1. Collect the original bytes using UTF-8 charset. This is to avoid double walking the tree if
   * the total size > 16MB This is to optimize for best case (see worst case as 4 below) that most of
   * the data will be < 16MB and only few offending varchars > 64KB.
   *
   * 2. Replace all TextNodes with Null nodes if they are greater than 64K.
   *
   * 3. Verify if replacing the varchars with NULLs brought the record size down to < 16MB. This
   * includes verifying the original bytes and transformed bytes are below the record size limit.
   *
   * 4. If 3 is false, this is the worst case scenarios where we try to resurrect PKs and cursors and
   * trash the rest of the record.
   *
   */
  @NotNull
  @Override
  public Pair<JsonNode, AirbyteRecordMessageMeta> transform(final StreamDescriptor streamDescriptor,
                                                            final JsonNode jsonNode,
                                                            final AirbyteRecordMessageMeta airbyteRecordMessageMeta) {
    final long startTime = System.currentTimeMillis();
    log.debug("Traversing the record to NULL fields for redshift size limitations");
    final String namespace =
        (streamDescriptor.getNamespace() != null && !streamDescriptor.getNamespace().isEmpty()) ? streamDescriptor.getNamespace() : defaultNamespace;
    final StreamConfig streamConfig = parsedCatalog.getStream(namespace, streamDescriptor.getName());
    final Optional<String> cursorField = streamConfig.getCursor().map(ColumnId::getOriginalName);
    // convert List<ColumnId> to Set<ColumnId> for faster lookup
    final Set<String> primaryKeys = streamConfig.getPrimaryKey().stream().map(ColumnId::getOriginalName).collect(Collectors.toSet());
    final DestinationSyncMode syncMode = streamConfig.getDestinationSyncMode();
    final TransformationInfo transformationInfo = transformNodes(jsonNode, DEFAULT_PREDICATE_VARCHAR_GREATER_THAN_64K);
    final int originalBytes = transformationInfo.originalBytes;
    final int transformedBytes = transformationInfo.originalBytes - transformationInfo.removedBytes;
    // We check if the transformedBytes has solved the record limit.
    log.debug("Traversal complete in {} ms", System.currentTimeMillis() - startTime);
    if (DEFAULT_PREDICATE_RECORD_SIZE_GT_THAN_16M.test(originalBytes)
        && DEFAULT_PREDICATE_RECORD_SIZE_GT_THAN_16M.test(transformedBytes)) {
      // If we have reached here with a bunch of small varchars constituted to becoming a large record,
      // person using Redshift for this data should re-evaluate life choices.
      log.warn("Record size before transformation {}, after transformation {} bytes exceeds 16MB limit", originalBytes, transformedBytes);
      final JsonNode minimalNode = constructMinimalJsonWithPks(jsonNode, primaryKeys, cursorField);
      if (minimalNode.isEmpty() && syncMode == DestinationSyncMode.APPEND_DEDUP) {
        // Fail the sync if PKs are missing in DEDUPE, no point sending an empty record to destination.
        throw new RuntimeException("Record exceeds size limit, cannot transform without PrimaryKeys in DEDUPE sync");
      }
      // Preserve original changes
      final List<AirbyteRecordMessageMetaChange> changes = new ArrayList<>();
      changes.add(new AirbyteRecordMessageMetaChange()
          .withField("all").withChange(Change.NULLED)
          .withReason(Reason.DESTINATION_RECORD_SIZE_LIMITATION));
      if (airbyteRecordMessageMeta != null && airbyteRecordMessageMeta.getChanges() != null) {
        changes.addAll(airbyteRecordMessageMeta.getChanges());
      }
      return new Pair<>(minimalNode, new AirbyteRecordMessageMeta().withChanges(changes));
    }
    if (airbyteRecordMessageMeta != null && airbyteRecordMessageMeta.getChanges() != null) {
      // The underlying list of AirbyteRecordMessageMeta is mutable
      transformationInfo.meta.getChanges().addAll(airbyteRecordMessageMeta.getChanges());
    }
    // We intentionally don't deep copy for transformation to avoid memory bloat.
    // The caller already has the reference of original jsonNode but returning again in
    // case we choose to deepCopy in future for thread-safety.
    return new Pair<>(jsonNode, transformationInfo.meta);
  }

  private ScalarNodeModification shouldTransformScalarNode(final JsonNode node,
                                                           final Predicate<String> textNodePredicate) {
    final int bytes;
    if (node.isTextual()) {
      final int originalBytes = getByteSize(node.asText()) + 2; // for quotes
      if (textNodePredicate.test(node.asText())) {
        return new ScalarNodeModification(originalBytes, // size before nulling
            originalBytes - 4, // account 4 bytes for null string
            true);
      }
      bytes = originalBytes;
    } else if (node.isNumber()) {
      // Serialize exactly for numbers to account for Scientific notation converted to full value.
      // This is what we send over wire for persistence.
      bytes = getByteSize(Jsons.serialize(node));
    } else if (node.isBoolean()) {
      bytes = getByteSize(node.toString());
    } else if (node.isNull()) {
      bytes = 4; // for "null"
    } else {
      bytes = 0;
    }
    return new ScalarNodeModification(bytes, // For all other types, just return bytes
        0,
        false);
  }

  private static int getByteSize(final String value) {
    return value.getBytes(StandardCharsets.UTF_8).length;
  }

  @VisibleForTesting
  TransformationInfo transformNodes(final JsonNode rootNode,
                                    final Predicate<String> textNodePredicate) {

    // Walk the tree and transform Varchars that exceed the limit
    // We are intentionally not checking the whole size upfront to check if it exceeds 16MB limit to
    // optimize for best case.
    int originalBytes = 0;
    int removedBytes = 0;
    // We accumulate nested keys in jsonPath format for adding to airbyte changes.
    final Deque<ImmutablePair<String, JsonNode>> stack = new ArrayDeque<>();
    final List<AirbyteRecordMessageMetaChange> changes = new ArrayList<>();

    // This was intentionally done using Iterative DFS to avoid stack overflow for large records.
    // This will ensure we are allocating on heap and not on stack.
    stack.push(ImmutablePair.of("$", rootNode));
    while (!stack.isEmpty()) {
      final ImmutablePair<String, JsonNode> jsonPathNodePair = stack.pop();
      final JsonNode currentNode = jsonPathNodePair.right;
      if (currentNode.isObject()) {
        originalBytes += CURLY_BRACES_BYTE_SIZE;
        final Iterator<Entry<String, JsonNode>> fields = currentNode.fields();
        while (fields.hasNext()) {
          final Map.Entry<String, JsonNode> field = fields.next();
          originalBytes += getByteSize(field.getKey()) + OBJECT_COLON_QUOTES_COMMA_BYTE_SIZE; // for quotes, colon, comma
          final String jsonPathKey = String.format("%s.%s", jsonPathNodePair.left, field.getKey());
          // TODO: Little difficult to unify this logic in Object & Array, find a way later
          // Push only non-scalar nodes to stack. For scalar nodes, we need reference of parent to do in-place
          // update.
          if (field.getValue().isContainerNode()) {
            stack.push(ImmutablePair.of(jsonPathKey, field.getValue()));
          } else {
            final ScalarNodeModification shouldTransform = shouldTransformScalarNode(field.getValue(), textNodePredicate);
            if (shouldTransform.shouldNull()) {
              removedBytes += shouldTransform.removedSize;
              // DO NOT do this if this code every modified to a multithreading call stack
              field.setValue(Jsons.jsonNode(null));
              changes.add(new AirbyteRecordMessageMetaChange()
                  .withField(jsonPathKey)
                  .withChange(Change.NULLED)
                  .withReason(Reason.DESTINATION_FIELD_SIZE_LIMITATION));
            }
            originalBytes += shouldTransform.size;
          }
        }
        originalBytes -= 1; // remove extra comma from last key-value pair
      } else if (currentNode.isArray()) {
        originalBytes += SQUARE_BRACKETS_BYTE_SIZE;
        final ArrayNode arrayNode = (ArrayNode) currentNode;
        // We cannot use foreach here as we need to update the array in place.
        for (int i = 0; i < arrayNode.size(); i++) {
          final JsonNode childNode = arrayNode.get(i);
          final String jsonPathKey = String.format("%s[%d]", jsonPathNodePair.left, i);
          if (childNode.isContainerNode())
            stack.push(ImmutablePair.of(jsonPathKey, childNode));
          else {
            final ScalarNodeModification shouldTransform = shouldTransformScalarNode(childNode, textNodePredicate);
            if (shouldTransform.shouldNull()) {
              removedBytes += shouldTransform.removedSize;
              // DO NOT do this if this code every modified to a multithreading call stack
              arrayNode.set(i, Jsons.jsonNode(null));
              changes.add(new AirbyteRecordMessageMetaChange()
                  .withField(jsonPathKey)
                  .withChange(Change.NULLED)
                  .withReason(Reason.DESTINATION_FIELD_SIZE_LIMITATION));
            }
            originalBytes += shouldTransform.size;
          }
        }
        originalBytes += !currentNode.isEmpty() ? currentNode.size() - 1 : 0; // for commas
      } else { // Top level scalar node is a valid json
        originalBytes += shouldTransformScalarNode(currentNode, textNodePredicate).size();
      }
    }

    if (removedBytes != 0) {
      log.info("Original record size {} bytes, Modified record size {} bytes", originalBytes, (originalBytes - removedBytes));
    }
    return new TransformationInfo(originalBytes, removedBytes, rootNode, new AirbyteRecordMessageMeta().withChanges(changes));
  }

  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  private JsonNode constructMinimalJsonWithPks(JsonNode rootNode, Set<String> primaryKeys, Optional<String> cursorField) {
    final ObjectNode minimalNode = (ObjectNode) Jsons.emptyObject();
    // We only iterate for top-level fields in the root object, since we only support PKs and cursor in
    // top level keys.
    if (rootNode.isObject()) {
      final Iterator<Entry<String, JsonNode>> fields = rootNode.fields();
      while (fields.hasNext()) {
        final Map.Entry<String, JsonNode> field = fields.next();
        if (!field.getValue().isContainerNode()) {
          if (primaryKeys.contains(field.getKey()) || cursorField.isPresent() && cursorField.get().equals(field.getKey())) {
            // Make a deepcopy into minimalNode of PKs and cursor fields and values,
            // without deepcopy, we will re-reference the original Tree's nodes.
            // god help us if someone set a PK on non-scalar field, and it reached this point, only do at root
            // level
            minimalNode.set(field.getKey(), field.getValue().deepCopy());
          }
        }
      }
    } else {
      log.error("Encountered {} as top level JSON field, this is not supported", rootNode.getNodeType());
      // This should have caught way before it reaches here. Just additional safety.
      throw new RuntimeException("Encountered " + rootNode.getNodeType() + " as top level JSON field, this is not supported");
    }
    return minimalNode;
  }

}
