/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp;

import com.fasterxml.jackson.databind.JsonNode;
import com.jcraft.jsch.ChannelSftp;
import com.jcraft.jsch.ChannelSftp.LsEntry;
import com.jcraft.jsch.SftpException;
import io.airbyte.integrations.source.sftp.enums.SupportedFileExtension;
import io.airbyte.integrations.source.sftp.parsers.SftpFileParser;
import io.airbyte.integrations.source.sftp.parsers.SftpFileParserFactory;
import io.airbyte.integrations.source.sftp.util.JsonSchemaGenerator;
import java.io.ByteArrayInputStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.Vector;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.apache.commons.io.FilenameUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SftpCommand {

  protected static final Logger LOGGER = LoggerFactory.getLogger(SftpClient.class);

  private static final String FILE_TYPE_SEPARATOR = ",";
  private final SftpClient client;
  private final Set<SupportedFileExtension> selectedFileExtensions;
  private final Pattern filePattern;
  private final SftpFileParserFactory sftpFileParserFactory;

  public SftpCommand(SftpClient client, JsonNode config) {
    this.client = client;
    sftpFileParserFactory = new SftpFileParserFactory();
    String commaSeparatedFileExtension = config.has("file_types") ? config.get("file_types").asText() : "";
    Set<String> selectedFileExtension = Set.of(commaSeparatedFileExtension.split(FILE_TYPE_SEPARATOR));
    selectedFileExtensions = selectedFileExtension.stream()
        .map(this::transformFileExtension)
        .collect(Collectors.toSet());
    filePattern = Pattern.compile(config.has("file_pattern") ? config.get("file_pattern").asText() : "");
  }

  private SupportedFileExtension transformFileExtension(String fileExtension) {
    try {
      return SupportedFileExtension.valueOf(fileExtension.toUpperCase());
    } catch (Exception e) {
      LOGGER.error("Unsupported file extension : {}", fileExtension);
      throw new RuntimeException();
    }
  }

  public void tryChangeWorkingDirectory(String path) {
    try {
      checkIfConnected();
      client.changeWorkingDirectory(FilenameUtils.normalize(path));
      LOGGER.info("Working directory set to : {}", path);
    } catch (SftpException e) {
      LOGGER.error("Could not find path : {} : ", path, e);
      throw new RuntimeException(e);
    }
  }

  public Map<String, JsonNode> getFilesSchemas() {
    checkIfConnected();
    Map<String, JsonNode> fileSchemas = new HashMap<>();
    Set<String> fileNames = getFileNames();
    LOGGER.info("Found file for sync : {}", fileNames);
    fileNames.forEach(fileName -> {
      ByteArrayInputStream file = client.getFile(fileName);
      JsonNode parsedFile = tryGetFirstNode(file, fileName);
      JsonNode schema = tryGetSchema(parsedFile, fileName);
      fileSchemas.put(fileName, schema);
    });
    return fileSchemas;
  }

  @SuppressWarnings("unchecked")
  private Set<String> getFileNames() {
    checkIfConnected();
    Vector<LsEntry> entries = new Vector<>();
    for (SupportedFileExtension fileExtension : selectedFileExtensions) {
      entries.addAll(client.lsFile(fileExtension));
    }
    return entries.stream()
        .map(ChannelSftp.LsEntry::getFilename)
        .filter(filePattern.asPredicate())
        .collect(Collectors.toSet());
  }

  private JsonNode tryGetSchema(JsonNode jsonNode, String fileName) {
    try {
      return JsonSchemaGenerator.getJsonSchema(jsonNode);
    } catch (Exception e) {
      LOGGER.error("Exception occurred while trying to parse schema of file {} : ", fileName, e);
      throw new RuntimeException(e);
    }
  }

  public JsonNode tryGetFirstNode(ByteArrayInputStream file, String fileName) {
    try {
      String extension = FilenameUtils.getExtension(fileName);
      SftpFileParser parser = sftpFileParserFactory.create(transformFileExtension(extension));
      return parser.parseFileFirstEntity(file);
    } catch (Exception e) {
      LOGGER.error("Exception occurred while trying to parse file {} : ", fileName, e);
      throw new RuntimeException();
    }
  }

  public List<JsonNode> getFileData(String fileName) {
    ByteArrayInputStream file = client.getFile(fileName);
    try {
      String extension = FilenameUtils.getExtension(fileName);
      SftpFileParser parser = sftpFileParserFactory.create(transformFileExtension(extension));
      return parser.parseFile(file);
    } catch (Exception e) {
      LOGGER.error("Exception occurred while trying to parse file {} : ", fileName, e);
      throw new RuntimeException();
    }
  }

  private void checkIfConnected() {
    if (!client.isConnected()) {
      LOGGER.info("SFTP client is not connected. Attempting to reconnect.");
      client.connect();
    }
  }

}
