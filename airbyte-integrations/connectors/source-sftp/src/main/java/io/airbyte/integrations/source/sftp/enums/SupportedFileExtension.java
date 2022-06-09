/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp.enums;

public enum SupportedFileExtension {

  CSV("csv"),
  JSON("json");

  public final String typeName;

  SupportedFileExtension(String typeName) {
    this.typeName = typeName;
  }

}
