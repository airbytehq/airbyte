/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp.parsers;

import io.airbyte.integrations.source.sftp.enums.SupportedFileExtension;

public class SftpFileParserFactory {

  public static SftpFileParser createInstance(SupportedFileExtension fileExtension) {
    switch (fileExtension) {
      case JSON -> {
        return new JsonFileParser();
      }
      case CSV -> {
        return new CsvFileParser();
      }
      default -> throw new RuntimeException("Unsupported file type");
    }
  }

}
