/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp.parsers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.List;

public class JsonFileParser implements SftpFileParser {

  private final ObjectMapper mapper = MoreMappers.initMapper();

  @Override
  public List<JsonNode> parseFile(ByteArrayInputStream file) throws IOException {
    return List.of(mapper.readValue(file, JsonNode.class));
  }

  @Override
  public JsonNode parseFileFirstEntity(ByteArrayInputStream file) throws IOException {
    return mapper.readValue(file, JsonNode.class);
  }

}
