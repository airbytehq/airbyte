/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp.parsers;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.List;

public interface SftpFileParser {

  /**
   * Parse the given inputStream file to List of JsonNode
   * <p>
   *
   * @param file the file for parsing
   * @return a {@link List} of {@link JsonNode jsonNodes}
   * @throws IOException if given file is not valid
   */
  List<JsonNode> parseFile(ByteArrayInputStream file) throws IOException;

  /**
   * Parse first entity from the given inputStream file to JsonNode
   * <p>
   *
   * @param file the file for parsing
   * @return a {@link JsonNode}
   * @throws IOException if given file is not valid
   */
  JsonNode parseFileFirstEntity(ByteArrayInputStream file) throws IOException;

}
