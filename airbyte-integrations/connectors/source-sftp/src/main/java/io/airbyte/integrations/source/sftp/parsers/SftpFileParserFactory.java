/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp.parsers;

// import static io.airbyte.integrations.source.sftp.enums.SupportedFileExtension.JSON;

import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.source.sftp.enums.SupportedFileExtension;
import java.util.Map;

public class SftpFileParserFactory {

  private final Map<SupportedFileExtension, SftpFileParser> SFTP_FILE_PARSER_MAPPING;

  public SftpFileParserFactory() {
    SFTP_FILE_PARSER_MAPPING = ImmutableMap.<SupportedFileExtension, SftpFileParser>builder()
        .put(SupportedFileExtension.JSON, new JsonFileParser())
        .put(SupportedFileExtension.CSV, new CsvFileParser())
        .build();
  }

  public SftpFileParser create(SupportedFileExtension fileExtension) {
    if (SFTP_FILE_PARSER_MAPPING.containsKey(fileExtension)) {
      return SFTP_FILE_PARSER_MAPPING.get(fileExtension);
    } else {
      throw new IllegalStateException(
          String.format("Unsupported file type : %s. Please choose from supported types : %s",
              fileExtension,
              SFTP_FILE_PARSER_MAPPING));
    }
  }

}
