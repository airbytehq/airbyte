/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.record_buffer.BaseSerializedBuffer;
import io.airbyte.integrations.destination.record_buffer.BufferCreateFunction;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.util.Flattening;
import io.airbyte.integrations.destination.s3.util.Stringify;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Callable;

public class JsonLSerializedBuffer extends BaseSerializedBuffer {

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();

  private PrintWriter printWriter;

  private final boolean flattenData;

  private final boolean stringifyData;

  protected JsonLSerializedBuffer(final BufferStorage bufferStorage, final boolean gzipCompression, final boolean flattenData, final boolean stringifyData) throws Exception {
    super(bufferStorage);
    // we always want to compress jsonl files
    withCompression(gzipCompression);
    this.flattenData = flattenData;
    this.stringifyData = stringifyData;
  }

  @Override
  protected void initWriter(final OutputStream outputStream) {
    printWriter = new PrintWriter(outputStream, true, StandardCharsets.UTF_8);
  }

  @Override
  protected void writeRecord(final AirbyteRecordMessage recordMessage) {
    final ObjectNode json = MAPPER.createObjectNode();
    json.put(JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString());
    json.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt());
    if (flattenData) {
      final Map<String, JsonNode> data = MAPPER.convertValue(recordMessage.getData(), new TypeReference<>() {});
      json.setAll(data);
    } else {
      json.set(JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getData());
    }
    // We want all root level objects as strings, including _airbyte_data
    if (stringifyData) {
      // Get the names of all the root level objects in the "json" ObjectNode
      try {
        JsonNode rootNode = MAPPER.readTree(json.toString());
        rootNode.fieldNames().forEachRemaining(fieldName -> {
          JsonNode node = rootNode.get(fieldName);
          if (node.isObject()) {
            // Convert the root level object to a string
            String jsonString = node.toString();

            // Set the value of the root level object in the "json" ObjectNode as a string
            json.put(fieldName, jsonString);
          }
        });
      } catch (JsonProcessingException e) {
        throw new RuntimeException(e);
      }
    }
    printWriter.println(Jsons.serialize(json));
  }

  @Override
  protected void flushWriter() {
    printWriter.flush();
  }

  @Override
  protected void closeWriter() {
    printWriter.close();
  }

  public static BufferCreateFunction createBufferFunction(final S3JsonlFormatConfig config,
                                                          final Callable<BufferStorage> createStorageFunction) {
    return (final AirbyteStreamNameNamespacePair stream, final ConfiguredAirbyteCatalog catalog) -> {
      final CompressionType compressionType = config == null
          ? S3DestinationConstants.DEFAULT_COMPRESSION_TYPE
          : config.getCompressionType();

      final Flattening flattening = config == null
          ? Flattening.NO
          : config.getFlatteningType();

      final Stringify stringify = config == null
              ? Stringify.NO
              : config.getStringifyType();
      return new JsonLSerializedBuffer(createStorageFunction.call(), compressionType != CompressionType.NO_COMPRESSION,
          flattening != Flattening.NO, stringify != Stringify.NO);
    };

  }

}
