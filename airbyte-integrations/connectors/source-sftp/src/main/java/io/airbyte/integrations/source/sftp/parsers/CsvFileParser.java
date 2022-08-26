/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp.parsers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.MappingIterator;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.dataformat.csv.CsvMapper;
import com.fasterxml.jackson.dataformat.csv.CsvSchema;
import io.airbyte.commons.jackson.MoreMappers;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class CsvFileParser implements SftpFileParser {

  private final CsvMapper csvMapper = new CsvMapper();
  private final ObjectMapper objectMapper = MoreMappers.initMapper();

  @Override
  public List<JsonNode> parseFile(ByteArrayInputStream file) throws IOException {
    final List<JsonNode> result = new ArrayList<>();
    final CsvSchema schema = CsvSchema.emptySchema().withHeader();
    final MappingIterator<Map<?, ?>> mappingIterator = csvMapper.readerFor(Map.class).with(schema).readValues(file);
    final ArrayNode arrayNode = objectMapper.valueToTree(mappingIterator.readAll());
    arrayNode.forEach(result::add);
    return result;
  }

  @Override
  public JsonNode parseFileFirstEntity(ByteArrayInputStream file) throws IOException {
    final CsvSchema schema = CsvSchema.emptySchema().withHeader();
    final MappingIterator<Map<?, ?>> mappingIterator = csvMapper.readerFor(Map.class).with(schema).readValues(file);
    return objectMapper.valueToTree(mappingIterator.next());
  }

}
